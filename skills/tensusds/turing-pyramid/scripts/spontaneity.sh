#!/bin/bash
# Turing Pyramid — Spontaneity Layer A: Surplus Energy System
# Sourced by run-cycle.sh — provides surplus accumulation and matrix shifting
#
# When all needs are satisfied (homeostasis), agents tend to always pick
# low-impact actions. This layer allows high-impact actions to "leak through"
# by accumulating surplus energy over time and shifting the impact matrix
# toward bigger actions when enough surplus builds up.
#
# Design: global gate (all needs >= 1.5) + per-need surplus pools
# Integration: modifies roll_impact_range() output, not a separate module

# ─── Configuration defaults ───
SPONT_BASELINE="${SPONT_BASELINE:-2.0}"
SPONT_GATE_MIN="${SPONT_GATE_MIN:-1.5}"
SPONT_DEFAULT_THRESHOLD="${SPONT_DEFAULT_THRESHOLD:-10}"
SPONT_DEFAULT_CAP="${SPONT_DEFAULT_CAP:-48}"
SPONT_MAX_SPEND_RATIO="${SPONT_MAX_SPEND_RATIO:-0.8}"
SPONT_MISS_RATIO="${SPONT_MISS_RATIO:-0.3}"

# ─── Gate Check ───
# Returns 0 (true) if spontaneity is possible, 1 (false) otherwise
# Gate requires: all needs >= gate_min AND starvation guard not active
check_spontaneity_gate() {
    local state_file=$1
    local config_file=$2
    local starvation_active=${3:-false}

    if [[ "$starvation_active" == "true" ]]; then
        return 1
    fi

    # Read gate_min from config, fallback to default
    local gate_min
    gate_min=$(jq -r '.settings.spontaneity.gate_min_satisfaction // empty' "$config_file" 2>/dev/null)
    gate_min="${gate_min:-$SPONT_GATE_MIN}"

    # Check all needs
    local needs
    needs=$(jq -r '.needs | keys[]' "$config_file")
    
    while IFS= read -r need; do
        local sat
        sat=$(jq -r --arg n "$need" '.[$n].satisfaction // 2.0' "$state_file")
        if (( $(echo "$sat < $gate_min" | bc -l) )); then
            return 1
        fi
    done <<< "$needs"

    return 0
}

# ─── Surplus Accumulation ───
# Called once per cycle, AFTER decay/tension calc, BEFORE action selection
# Accumulates surplus for each need with spontaneity enabled
accumulate_surplus() {
    local state_file=$1
    local config_file=$2
    local starvation_active=${3:-false}

    # Check global gate
    if ! check_spontaneity_gate "$state_file" "$config_file" "$starvation_active"; then
        # Gate closed: surplus freezes (does NOT reset)
        return 0
    fi

    # Check if spontaneity is enabled globally
    local spont_enabled
    spont_enabled=$(jq -r '.settings.spontaneity.enabled // false' "$config_file" 2>/dev/null)
    if [[ "$spont_enabled" != "true" ]]; then
        return 0
    fi

    local baseline
    baseline=$(jq -r '.settings.spontaneity.baseline // empty' "$config_file" 2>/dev/null)
    baseline="${baseline:-$SPONT_BASELINE}"

    local now_epoch
    now_epoch=$(date +%s)
    local now_iso
    now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local needs
    needs=$(jq -r '.needs | keys[]' "$config_file")

    while IFS= read -r need; do
        # Check if this need has spontaneity config
        local spont_cfg
        spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")
        
        if [[ "$spont_cfg" == "null" ]]; then
            continue
        fi

        local spont_enabled_need
        spont_enabled_need=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
        if [[ "$spont_enabled_need" != "true" ]]; then
            continue
        fi

        local cap
        cap=$(jq -r ".needs.\"$need\".spontaneous.cap // $SPONT_DEFAULT_CAP" "$config_file")

        # Get current satisfaction and surplus
        local sat
        sat=$(jq -r --arg n "$need" '.[$n].satisfaction // 2.0' "$state_file")
        
        local current_surplus
        current_surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")

        # Calculate hours since last surplus check
        local last_check
        last_check=$(jq -r --arg n "$need" '.[$n].last_surplus_check // "1970-01-01T00:00:00Z"' "$state_file")
        local last_epoch
        last_epoch=$(date -d "$last_check" +%s 2>/dev/null || echo 0)
        local seconds_since=$((now_epoch - last_epoch))
        local hours_since
        hours_since=$(echo "scale=4; $seconds_since / 3600" | bc -l)

        # Skip if less than 1 minute since last check (avoid micro-accumulation)
        if (( seconds_since < 60 )); then
            continue
        fi

        # Delta = (satisfaction - baseline) * hours
        # Can be negative if sat < baseline (surplus drains)
        local delta
        delta=$(echo "scale=4; ($sat - $baseline) * $hours_since" | bc -l)

        # Apply delta and clamp
        local new_surplus
        new_surplus=$(echo "scale=4; $current_surplus + $delta" | bc -l)
        
        # Clamp to [0, cap]
        if (( $(echo "$new_surplus < 0" | bc -l) )); then
            new_surplus="0"
        fi
        if (( $(echo "$new_surplus > $cap" | bc -l) )); then
            new_surplus="$cap"
        fi

        # Round to 1 decimal for cleanliness
        new_surplus=$(printf "%.1f" "$new_surplus")

        # Update state
        jq --arg n "$need" \
           --argjson s "$new_surplus" \
           --arg t "$now_iso" \
           '.[$n].surplus = $s | .[$n].last_surplus_check = $t' \
           "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"

        # Debug log (only if delta is meaningful)
        if (( $(echo "${delta#-} > 0.01" | bc -l) )); then
            echo "  [SURPLUS:ACCUM] $need: sat=$sat, delta=$(printf "%+.2f" "$delta"), surplus=$new_surplus/$cap"
        fi

    done <<< "$needs"
}

# ─── Random float in range ───
# Returns random float between min and max (inclusive)
random_float() {
    local min=$1
    local max=$2
    # Use $RANDOM (0-32767) for randomness
    local rand=$RANDOM
    local range
    range=$(echo "scale=4; $max - $min" | bc -l)
    local result
    result=$(echo "scale=4; $min + ($rand / 32767) * $range" | bc -l)
    printf "%.2f" "$result"
}

# ─── Get Shifted Matrix ───
# If surplus is eligible, interpolate impact matrix toward spontaneous target
# Outputs: "shifted_low shifted_mid shifted_high spend_amount t_value" or "none"
get_shifted_matrix() {
    local need=$1
    local normal_low=$2
    local normal_mid=$3
    local normal_high=$4
    local state_file=$5
    local config_file=$6

    # Check if spontaneity configured for this need
    local spont_cfg
    spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")
    if [[ "$spont_cfg" == "null" ]]; then
        echo "none"
        return
    fi

    local spont_enabled
    spont_enabled=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
    if [[ "$spont_enabled" != "true" ]]; then
        echo "none"
        return
    fi

    # Get surplus and config
    local surplus
    surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")
    
    local threshold
    threshold=$(jq -r ".needs.\"$need\".spontaneous.threshold // $SPONT_DEFAULT_THRESHOLD" "$config_file")
    
    local cap
    cap=$(jq -r ".needs.\"$need\".spontaneous.cap // $SPONT_DEFAULT_CAP" "$config_file")

    local max_spend_ratio
    max_spend_ratio=$(jq -r '.settings.spontaneity.max_spend_ratio // empty' "$config_file" 2>/dev/null)
    max_spend_ratio="${max_spend_ratio:-$SPONT_MAX_SPEND_RATIO}"

    # Calculate max_spend
    local max_spend
    max_spend=$(echo "scale=4; $surplus * $max_spend_ratio" | bc -l)

    # Both conditions: surplus >= threshold AND max_spend >= threshold
    if (( $(echo "$surplus < $threshold" | bc -l) )) || \
       (( $(echo "$max_spend < $threshold" | bc -l) )); then
        echo "none"
        return
    fi

    # Get target matrix
    local target_low target_mid target_high
    target_low=$(jq -r ".needs.\"$need\".spontaneous.target_matrix.low // 10" "$config_file")
    target_mid=$(jq -r ".needs.\"$need\".spontaneous.target_matrix.mid // 30" "$config_file")
    target_high=$(jq -r ".needs.\"$need\".spontaneous.target_matrix.high // 60" "$config_file")

    # Roll: how much surplus to risk
    local min_spend="$threshold"
    local rolled_spend
    rolled_spend=$(random_float "$min_spend" "$max_spend")

    # Interpolation factor t = rolled / cap, clamped to [0, 1]
    local t
    t=$(echo "scale=4; $rolled_spend / $cap" | bc -l)
    if (( $(echo "$t > 1.0" | bc -l) )); then t="1.0"; fi

    # Interpolate: normal + (target - normal) * t
    local shifted_low shifted_mid shifted_high
    shifted_low=$(echo "scale=1; $normal_low + ($target_low - $normal_low) * $t" | bc -l)
    shifted_mid=$(echo "scale=1; $normal_mid + ($target_mid - $normal_mid) * $t" | bc -l)
    shifted_high=$(echo "scale=1; $normal_high + ($target_high - $normal_high) * $t" | bc -l)

    # Round to integers
    shifted_low=$(printf "%.0f" "$shifted_low")
    shifted_mid=$(printf "%.0f" "$shifted_mid")
    shifted_high=$(printf "%.0f" "$shifted_high")

    # Normalize to sum=100
    local total=$((shifted_low + shifted_mid + shifted_high))
    if [[ $total -ne 100 ]] && [[ $total -gt 0 ]]; then
        # Adjust the largest bucket
        local diff=$((100 - total))
        if [[ $shifted_high -ge $shifted_low ]] && [[ $shifted_high -ge $shifted_mid ]]; then
            shifted_high=$((shifted_high + diff))
        elif [[ $shifted_mid -ge $shifted_low ]]; then
            shifted_mid=$((shifted_mid + diff))
        else
            shifted_low=$((shifted_low + diff))
        fi
    fi

    echo "$shifted_low $shifted_mid $shifted_high $rolled_spend $t"
}

# ─── Spend Surplus ───
# Called after action selection to deduct surplus
spend_surplus() {
    local need=$1
    local impact_range=$2     # "low", "mid", "high"
    local rolled_spend=$3
    local state_file=$4
    local config_file=$5

    local miss_ratio
    miss_ratio=$(jq -r '.settings.spontaneity.spend_on_miss_ratio // empty' "$config_file" 2>/dev/null)
    miss_ratio="${miss_ratio:-$SPONT_MISS_RATIO}"

    local current_surplus
    current_surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")

    local spend_amount
    if [[ "$impact_range" == "high" ]]; then
        # Full spend
        spend_amount="$rolled_spend"
        echo "  [SURPLUS] $need: → HIGH → surplus -= $spend_amount → $(echo "scale=1; $current_surplus - $spend_amount" | bc -l) [SPONTANEOUS]" >&2
    else
        # Partial spend (cost of attempt)
        spend_amount=$(echo "scale=2; $rolled_spend * $miss_ratio" | bc -l)
        echo "  [SURPLUS] $need: → $impact_range → surplus -= $spend_amount (miss) → $(echo "scale=1; $current_surplus - $spend_amount" | bc -l)" >&2
    fi

    # Apply deduction, clamp to 0
    local new_surplus
    new_surplus=$(echo "scale=1; $current_surplus - $spend_amount" | bc -l)
    if (( $(echo "$new_surplus < 0" | bc -l) )); then
        new_surplus="0"
    fi

    jq --arg n "$need" \
       --argjson s "$new_surplus" \
       '.[$n].surplus = $s' \
       "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"
}

# ─── Show Surplus Status ───
# For show-status.sh integration
show_surplus_status() {
    local state_file=$1
    local config_file=$2
    local starvation_active=${3:-false}

    local spont_enabled
    spont_enabled=$(jq -r '.settings.spontaneity.enabled // false' "$config_file" 2>/dev/null)
    if [[ "$spont_enabled" != "true" ]]; then
        return
    fi

    # Gate status
    local gate_status="CLOSED"
    if check_spontaneity_gate "$state_file" "$config_file" "$starvation_active"; then
        gate_status="OPEN"
    fi

    echo ""
    echo "Surplus pools (gate: $gate_status):"

    local needs
    needs=$(jq -r '.needs | keys[]' "$config_file")

    while IFS= read -r need; do
        local spont_cfg
        spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")

        if [[ "$spont_cfg" == "null" ]]; then
            printf "  %-16s — (spontaneity disabled)\n" "$need:"
            continue
        fi

        local spont_enabled_need
        spont_enabled_need=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
        if [[ "$spont_enabled_need" != "true" ]]; then
            printf "  %-16s — (spontaneity disabled)\n" "$need:"
            continue
        fi

        local surplus cap threshold
        surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")
        cap=$(jq -r ".needs.\"$need\".spontaneous.cap // $SPONT_DEFAULT_CAP" "$config_file")
        threshold=$(jq -r ".needs.\"$need\".spontaneous.threshold // $SPONT_DEFAULT_THRESHOLD" "$config_file")

        # Progress bar (12 chars)
        local filled
        filled=$(echo "scale=0; $surplus / $cap * 12" | bc -l 2>/dev/null)
        filled=${filled:-0}
        if [[ $filled -gt 12 ]]; then filled=12; fi
        local empty=$((12 - filled))
        local bar=""
        for ((i=0; i<filled; i++)); do bar+="█"; done
        for ((i=0; i<empty; i++)); do bar+="░"; done

        # Status label
        local max_spend
        max_spend=$(echo "scale=2; $surplus * $SPONT_MAX_SPEND_RATIO" | bc -l)
        local status_label
        if (( $(echo "$surplus >= $threshold" | bc -l) )) && \
           (( $(echo "$max_spend >= $threshold" | bc -l) )); then
            status_label="eligible ✓"
        elif (( $(echo "$surplus > 0" | bc -l) )); then
            status_label="accumulating..."
        else
            local sat
            sat=$(jq -r --arg n "$need" '.[$n].satisfaction // 2.0' "$state_file")
            if (( $(echo "$sat < $SPONT_BASELINE" | bc -l) )); then
                status_label="sat < baseline"
            else
                status_label="starting..."
            fi
        fi

        printf "  %-16s %s  %5.1f/%s  (%s)\n" "$need:" "$bar" "$surplus" "$cap" "$status_label"

    done <<< "$needs"
}
