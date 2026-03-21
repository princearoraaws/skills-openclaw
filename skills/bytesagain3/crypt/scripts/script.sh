#!/usr/bin/env bash
set -euo pipefail

# crypt — skill script
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

DATA_DIR="${HOME}/.crypt"
mkdir -p "$DATA_DIR"

show_help() {
    cat << 'HELPEOF'
crypt — command-line tool

Commands:
  encrypt        Run encrypt operation
  decrypt        Run decrypt operation
  hash           Run hash operation
  sign           Run sign operation
  verify         Run verify operation
  keygen         Run keygen operation
  encode         Run encode operation
  decode         Run decode operation
  password       Run password operation
  config         Run config operation
  stats      Show statistics
  export     Export data (json|csv|txt)
  search     Search across entries
  recent     Show recent entries
  status     Show current status
  help       Show this help message
  version    Show version number

Data stored in: ~/.crypt/
HELPEOF
}

show_version() {
    echo "crypt v1.0.0 — Powered by BytesAgain"
}

cmd_stats() {
    echo "=== crypt Statistics ==="
    local total=0
    for f in "$DATA_DIR"/*.log; do
        [ -f "$f" ] || continue
        local name=$(basename "$f" .log)
        local c=$(wc -l < "$f" 2>/dev/null || echo 0)
        total=$((total + c))
        echo "  $name: $c entries"
    done
    echo "  Total: $total entries"
    echo "  Data size: $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1 || echo 'N/A')"
    echo "  Since: $(head -1 "$DATA_DIR/history.log" 2>/dev/null | cut -d'|' -f1 || echo 'N/A')"
}

cmd_export() {
    local fmt="${1:-json}"
    local out="crypt-export.$fmt"
    case "$fmt" in
        json)
            echo "[" > "$out"
            local first=1
            for f in "$DATA_DIR"/*.log; do
                [ -f "$f" ] || continue
                while IFS= read -r line; do
                    [ $first -eq 1 ] && first=0 || echo "," >> "$out"
                    local ts=$(echo "$line" | cut -d'|' -f1)
                    local cmd=$(echo "$line" | cut -d'|' -f2)
                    local data=$(echo "$line" | cut -d'|' -f3-)
                    printf '  {"timestamp":"%s","command":"%s","data":"%s"}' "$ts" "$cmd" "$data" >> "$out"
                done < "$f"
            done
            echo "" >> "$out"
            echo "]" >> "$out"
            ;;
        csv)
            echo "timestamp,command,data" > "$out"
            for f in "$DATA_DIR"/*.log; do
                [ -f "$f" ] || continue
                while IFS= read -r line; do
                    echo "$line" | awk -F'|' '{printf "\"%s\",\"%s\",\"%s\"\n", $1, $2, $3}' >> "$out"
                done < "$f"
            done
            ;;
        txt)
            > "$out"
            for f in "$DATA_DIR"/*.log; do
                [ -f "$f" ] || continue
                echo "--- $(basename "$f" .log) ---" >> "$out"
                cat "$f" >> "$out"
                echo "" >> "$out"
            done
            ;;
        *)
            echo "Unknown format: $fmt (use json, csv, or txt)"
            return 1
            ;;
    esac
    echo "Exported to $out ($(wc -c < "$out" 2>/dev/null || echo 0) bytes)"
}

cmd_search() {
    local term="${1:-}"
    [ -z "$term" ] && { echo "Usage: crypt search <term>"; return 1; }
    echo "=== Search: $term ==="
    local found=0
    for f in "$DATA_DIR"/*.log; do
        [ -f "$f" ] || continue
        local matches=$(grep -i "$term" "$f" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            echo "--- $(basename "$f" .log) ---"
            echo "$matches"
            found=$((found + 1))
        fi
    done
    [ $found -eq 0 ] && echo "No matches found."
}

cmd_recent() {
    local n="${1:-10}"
    echo "=== Recent $n entries ==="
    for f in "$DATA_DIR"/*.log; do
        [ -f "$f" ] || continue
        tail -n "$n" "$f" 2>/dev/null
    done | sort -t'|' -k1 | tail -n "$n"
}

cmd_status() {
    echo "=== crypt Status ==="
    echo "  Entries: $(cat "$DATA_DIR"/*.log 2>/dev/null | wc -l || echo 0)"
    echo "  Disk: $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1 || echo 'N/A')"
    local last=$(tail -1 "$DATA_DIR/history.log" 2>/dev/null || echo "never")
    echo "  Last activity: $last"
}

# Main
CMD="${1:-help}"
shift 2>/dev/null || true

case "$CMD" in
    encrypt)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|encrypt|${*}" >> "$DATA_DIR/encrypt.log"
        local total=$(wc -l < "$DATA_DIR/encrypt.log" 2>/dev/null || echo 0)
        echo "[crypt] encrypt recorded (entry #$total)"
        ;;
    decrypt)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|decrypt|${*}" >> "$DATA_DIR/decrypt.log"
        local total=$(wc -l < "$DATA_DIR/decrypt.log" 2>/dev/null || echo 0)
        echo "[crypt] decrypt recorded (entry #$total)"
        ;;
    hash)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|hash|${*}" >> "$DATA_DIR/hash.log"
        local total=$(wc -l < "$DATA_DIR/hash.log" 2>/dev/null || echo 0)
        echo "[crypt] hash recorded (entry #$total)"
        ;;
    sign)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|sign|${*}" >> "$DATA_DIR/sign.log"
        local total=$(wc -l < "$DATA_DIR/sign.log" 2>/dev/null || echo 0)
        echo "[crypt] sign recorded (entry #$total)"
        ;;
    verify)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|verify|${*}" >> "$DATA_DIR/verify.log"
        local total=$(wc -l < "$DATA_DIR/verify.log" 2>/dev/null || echo 0)
        echo "[crypt] verify recorded (entry #$total)"
        ;;
    keygen)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|keygen|${*}" >> "$DATA_DIR/keygen.log"
        local total=$(wc -l < "$DATA_DIR/keygen.log" 2>/dev/null || echo 0)
        echo "[crypt] keygen recorded (entry #$total)"
        ;;
    encode)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|encode|${*}" >> "$DATA_DIR/encode.log"
        local total=$(wc -l < "$DATA_DIR/encode.log" 2>/dev/null || echo 0)
        echo "[crypt] encode recorded (entry #$total)"
        ;;
    decode)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|decode|${*}" >> "$DATA_DIR/decode.log"
        local total=$(wc -l < "$DATA_DIR/decode.log" 2>/dev/null || echo 0)
        echo "[crypt] decode recorded (entry #$total)"
        ;;
    password)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|password|${*}" >> "$DATA_DIR/password.log"
        local total=$(wc -l < "$DATA_DIR/password.log" 2>/dev/null || echo 0)
        echo "[crypt] password recorded (entry #$total)"
        ;;
    config)
        local ts=$(date '+%Y-%m-%d %H:%M')
        echo "$ts|config|${*}" >> "$DATA_DIR/config.log"
        local total=$(wc -l < "$DATA_DIR/config.log" 2>/dev/null || echo 0)
        echo "[crypt] config recorded (entry #$total)"
        ;;
    stats)
        cmd_stats
        ;;
    export)
        cmd_export "$@"
        ;;
    search)
        cmd_search "$@"
        ;;
    recent)
        cmd_recent "$@"
        ;;
    status)
        cmd_status
        ;;
    help|--help|-h)
        show_help
        ;;
    version|--version|-v)
        show_version
        ;;
    *)
        echo "Unknown command: $CMD"
        echo "Run 'crypt help' for usage."
        exit 1
        ;;
esac
