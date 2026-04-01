#!/usr/bin/env bash

set -euo pipefail

BASE_URL="https://pollenwechat.bjpws.com"
CITY_API="$BASE_URL/v1/weatherPollen/pollens"
STATIONS_API="$BASE_URL/api/pollen/obs/latestPollenLevels"

EXIT_DEPENDENCY=1
EXIT_USAGE=2
EXIT_UPSTREAM=3
EXIT_EMPTY=4

MODE="overview"
FORMAT="json"
LIMIT=5
STATION_ID=""
DISTRICT=""
TIMEOUT_MS=8000

# ---------------------------------------------------------------------------
# Shared jq definitions used across all build functions.
# ---------------------------------------------------------------------------
JQ_COMMON_DEFS='
def to_num:
  if . == null or . == "" then null
  else (try tonumber catch null)
  end;

def level_code_from_value($n):
  if $n == null then 0
  elif $n <= 100 then 1
  elif $n <= 250 then 2
  elif $n <= 400 then 3
  elif $n <= 800 then 4
  else 5
  end;

def level_text_from_code($code):
  if $code == 1 then "低"
  elif $code == 2 then "较低"
  elif $code == 3 then "中等"
  elif $code == 4 then "高"
  elif $code == 5 then "很高"
  else "暂无"
  end;

def normalized_area($source; $entity_id; $entity_name; $raw):
  ($raw | to_num) as $n
  | if $n == null then
      {
        raw_pollen: $raw,
        display_value: null,
        sort_value: -1,
        level_code: 0,
        level_text: "暂无",
        warning: null
      }
    elif $n >= 99999 then
      {
        raw_pollen: $raw,
        display_value: ">800",
        sort_value: 801,
        level_code: 5,
        level_text: "很高",
        warning: {
          code: "pollen_value_capped",
          source: $source,
          entity_id: $entity_id,
          entity_name: $entity_name,
          raw_pollen: $raw,
          message: "Detected capped or sentinel pollen value >= 99999; normalized to >800."
        }
      }
    else
      (level_code_from_value($n)) as $code
      | {
          raw_pollen: $raw,
          display_value: (if $n > 800 then ">800" else ($n | floor | tostring) end),
          sort_value: $n,
          level_code: $code,
          level_text: level_text_from_code($code),
          warning: null
        }
    end;

def normalized_station($source; $entity_id; $entity_name; $raw; $level_code):
  ($raw | to_num) as $n
  | ($level_code | to_num) as $source_code
  | (if ($source_code != null and $source_code >= 1 and $source_code <= 5)
      then $source_code
      else level_code_from_value($n)
     end) as $code
  | if $n == null then
      {
        raw_pollen: $raw,
        display_value: null,
        sort_value: -1,
        level_code: $code,
        level_text: level_text_from_code($code),
        warning: null
      }
    elif $n >= 99999 then
      {
        raw_pollen: $raw,
        display_value: ">800",
        sort_value: 801,
        level_code: $code,
        level_text: level_text_from_code($code),
        warning: {
          code: "pollen_value_capped",
          source: $source,
          entity_id: $entity_id,
          entity_name: $entity_name,
          raw_pollen: $raw,
          message: "Detected capped or sentinel pollen value >= 99999; normalized to >800."
        }
      }
    else
      {
        raw_pollen: $raw,
        display_value: (if $n > 800 then ">800" else ($n | floor | tostring) end),
        sort_value: $n,
        level_code: $code,
        level_text: level_text_from_code($code),
        warning: null
      }
    end;

def normalized_station_value($raw; $level_code):
  ($raw | to_num) as $n
  | ($level_code | to_num) as $source_code
  | (if ($source_code != null and $source_code >= 1 and $source_code <= 5)
      then $source_code
      else level_code_from_value($n)
     end) as $code
  | if $n == null then
      {
        raw_pollen: $raw,
        numeric_value: null,
        display_value: null,
        level_code: $code,
        level_text: level_text_from_code($code),
        warning: null
      }
    elif $n >= 99999 then
      {
        raw_pollen: $raw,
        numeric_value: $n,
        display_value: ">800",
        level_code: $code,
        level_text: level_text_from_code($code),
        warning: {
          code: "pollen_value_capped",
          source: "history_series",
          raw_pollen: $raw,
          message: "Detected capped or sentinel pollen value >= 99999; normalized to >800."
        }
      }
    else
      {
        raw_pollen: $raw,
        numeric_value: $n,
        display_value: (if $n > 800 then ">800" else ($n | floor | tostring) end),
        level_code: $code,
        level_text: level_text_from_code($code),
        warning: null
      }
    end;

def severity_from_code($code):
  if $code >= 5 then "very_high"
  elif $code == 4 then "high"
  else null
  end;
'

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

usage() {
  cat <<'EOF'
用法:
  beijing-pollen-query.sh query --mode overview [--limit <n>] [--timeout-ms <n>]
  beijing-pollen-query.sh query --mode stations [--timeout-ms <n>]
  beijing-pollen-query.sh query --mode history  --district <区名> [--timeout-ms <n>]
  beijing-pollen-query.sh query --mode report   --district <区名> [--limit <n>] [--format json|text] [--timeout-ms <n>]

模式:
  overview  北京全市区域概览和站点快照
  stations  全部站点实时读数
  history   单站点 24 小时历史（需要 --district）
  report    每日简报：概览 + 目标站点趋势（需要 --district）

参数:
  --district <区名>    区名，模糊匹配（如 海淀、海淀区、朝阳）
  --station-id <id>    站点 ID（history 模式的替代方式）
  --format json|text   输出格式（默认 json）
  --limit <n>          热点站点数量（默认 5）
  --timeout-ms <n>     HTTP 超时毫秒数（默认 8000）

说明:
  - 运行依赖: bash, curl, jq
  - 输出始终为 JSON（text 格式将可读文本包裹在 {"data":{"text":"..."}} 中）
  - 北京共 16 个固定监测站，每区一个
  - 可用区名: 东城 西城 朝阳 海淀 丰台 石景山 门头沟 房山 通州 顺义 昌平 大兴 怀柔 平谷 密云 延庆
EOF
}

timestamp_utc() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

timestamp_cst() {
  TZ=Asia/Shanghai date +"%Y-%m-%d %H:%M"
}

print_error_json_without_jq() {
  local code="$1"
  local message="$2"
  local generated_at
  generated_at="$(timestamp_utc)"
  printf '{"ok":false,"mode":null,"generated_at":"%s","query":{},"warnings":[],"error":{"code":"%s","message":"%s"}}\n' \
    "$generated_at" "$code" "$message"
}

print_error_json() {
  local exit_code="$1"
  local code="$2"
  local message="$3"
  local generated_at
  generated_at="$(timestamp_utc)"

  if command -v jq >/dev/null 2>&1; then
    jq -n \
      --arg generated_at "$generated_at" \
      --arg code "$code" \
      --arg message "$message" \
      '{
        ok: false,
        mode: null,
        generated_at: $generated_at,
        query: {},
        warnings: [],
        error: {
          code: $code,
          message: $message
        }
      }'
  else
    print_error_json_without_jq "$code" "$message"
  fi

  exit "$exit_code"
}

require_command() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    print_error_json "$EXIT_DEPENDENCY" "missing_dependency" "Missing required dependency: $cmd. $hint"
  fi
}

is_positive_integer() {
  local value="$1"
  [[ "$value" =~ ^[0-9]+$ ]] && (( value > 0 ))
}

timeout_seconds() {
  local ms="$1"
  printf '%d.%03d' "$((ms / 1000))" "$((ms % 1000))"
}

fetch_json() {
  local url="$1"
  local response

  if ! response="$(
    curl -fsS \
      --connect-timeout "$(timeout_seconds "$TIMEOUT_MS")" \
      --max-time "$(timeout_seconds "$TIMEOUT_MS")" \
      "$url"
  )"; then
    print_error_json "$EXIT_UPSTREAM" "upstream_request_failed" "Failed to fetch upstream API: $url"
  fi

  if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$response"; then
    print_error_json "$EXIT_UPSTREAM" "invalid_upstream_json" "Received invalid JSON from upstream API: $url"
  fi

  printf '%s' "$response"
}

validate_business_success() {
  local response="$1"
  local api_name="$2"
  local api_code api_msg

  api_code="$(jq -r '.code // empty' <<<"$response")"
  api_msg="$(jq -r '.msg // .message // "Unknown upstream error."' <<<"$response")"

  if [[ "$api_code" != "200" ]]; then
    print_error_json "$EXIT_UPSTREAM" "upstream_api_error" "$api_name returned code $api_code: $api_msg"
  fi
}

query_object_json() {
  jq -n \
    --arg mode "$MODE" \
    --arg format "$FORMAT" \
    --arg station_id "$STATION_ID" \
    --arg district "$DISTRICT" \
    --argjson limit "$LIMIT" \
    '{
      mode: $mode,
      format: $format,
      station_id: (if $station_id == "" then null else $station_id end),
      district: (if $district == "" then null else $district end),
      limit: $limit
    }'
}

# ---------------------------------------------------------------------------
# Resolve district name to station ID from stations API response.
# Fuzzy match: "海淀" matches "海淀区", "朝阳" matches "朝阳区".
# Prints: station_id or "null" on no match.
# ---------------------------------------------------------------------------
resolve_district_to_station_id() {
  local stations_json="$1"
  local district="$2"
  jq -r -n \
    --argjson stations "$stations_json" \
    --arg district "$district" \
    '($stations.data // [])
     | map(select(.staName | contains($district)))
     | first | .staId // "null"'
}

# ---------------------------------------------------------------------------
# Build functions — each uses JQ_COMMON_DEFS + mode-specific body
# ---------------------------------------------------------------------------

build_overview_json() {
  local city_json="$1"
  local stations_json="$2"
  local generated_at="$3"
  local query_json="$4"

  local overview_body
  read -r -d '' overview_body <<'JQ' || true

($city.data.beijing // []) as $areas_raw
| ($stations.data // []) as $stations_raw
| ($areas_raw | map(
    . as $row
    | normalized_area("beijing_area"; $row.areaId; $row.name; $row.pollen) as $norm
    | {
        area_id: $row.areaId,
        name: $row.name,
        raw_pollen: $norm.raw_pollen,
        display_value: $norm.display_value,
        level_code: $norm.level_code,
        level_text: $norm.level_text,
        observed_at: $row.dataTime,
        _sort_value: $norm.sort_value,
        _warning: $norm.warning
      }
  )) as $areas
| ($stations_raw | map(
    . as $row
    | normalized_station("station"; $row.staId; $row.staName; $row.hfH; $row.hfHLv) as $norm
    | {
        station_id: $row.staId,
        station_name: $row.staName,
        raw_pollen: $norm.raw_pollen,
        display_value: $norm.display_value,
        level_code: $norm.level_code,
        level_text: $norm.level_text,
        observed_at: $row.nttimeter,
        advice: $row.advice,
        _sort_value: $norm.sort_value,
        _warning: $norm.warning
      }
  )) as $station_rows
| ($areas | map(select(._warning != null) | ._warning)) as $area_warnings
| ($station_rows | map(select(._warning != null) | ._warning)) as $station_warnings
| ($areas
    | map(select(.level_code >= 4)
      | {
          source: "beijing_area",
          entity_id: .area_id,
          name: .name,
          severity: severity_from_code(.level_code),
          level_code,
          level_text,
          display_value,
          observed_at
        })
  ) as $area_alerts
| ($station_rows
    | map(select(.level_code >= 4)
      | {
          source: "station",
          entity_id: .station_id,
          name: .station_name,
          severity: severity_from_code(.level_code),
          level_code,
          level_text,
          display_value,
          observed_at,
          advice
        })
  ) as $station_alerts
| {
    ok: true,
    mode: "overview",
    generated_at: $generated_at,
    query: $query,
    data: {
      beijing_areas: ($areas | map(del(._sort_value, ._warning))),
      stations: ($station_rows | map(del(._sort_value, ._warning))),
      hotspots: (
        $station_rows
        | sort_by([.level_code, ._sort_value])
        | reverse
        | .[:$limit]
        | map(del(._sort_value, ._warning))
      ),
      alerts: ($area_alerts + $station_alerts)
    },
    warnings: ($area_warnings + $station_warnings)
  }
JQ

  jq -n \
    --argjson city "$city_json" \
    --argjson stations "$stations_json" \
    --argjson query "$query_json" \
    --arg generated_at "$generated_at" \
    --argjson limit "$LIMIT" \
    "${JQ_COMMON_DEFS}${overview_body}"
}

build_stations_json() {
  local stations_json="$1"
  local generated_at="$2"
  local query_json="$3"

  local stations_body
  read -r -d '' stations_body <<'JQ' || true

($stations.data // []) as $stations_raw
| ($stations_raw | map(
    . as $row
    | normalized_station("station"; $row.staId; $row.staName; $row.hfH; $row.hfHLv) as $norm
    | {
        station_id: $row.staId,
        station_name: $row.staName,
        raw_pollen: $norm.raw_pollen,
        display_value: $norm.display_value,
        level_code: $norm.level_code,
        level_text: $norm.level_text,
        observed_at: $row.nttimeter,
        advice: $row.advice,
        _sort_value: $norm.sort_value,
        _warning: $norm.warning
      }
  )) as $station_rows
| {
    ok: true,
    mode: "stations",
    generated_at: $generated_at,
    query: $query,
    data: {
      stations: ($station_rows | map(del(._sort_value, ._warning))),
      alerts: (
        $station_rows
        | map(select(.level_code >= 4)
          | {
              source: "station",
              entity_id: .station_id,
              name: .station_name,
              severity: severity_from_code(.level_code),
              level_code,
              level_text,
              display_value,
              observed_at,
              advice
            })
      )
    },
    warnings: ($station_rows | map(select(._warning != null) | ._warning))
  }
JQ

  jq -n \
    --argjson stations "$stations_json" \
    --argjson query "$query_json" \
    --arg generated_at "$generated_at" \
    "${JQ_COMMON_DEFS}${stations_body}"
}

build_history_json() {
  local history_json="$1"
  local generated_at="$2"
  local query_json="$3"

  local history_body
  read -r -d '' history_body <<'JQ' || true

($history.data // []) as $rows
| ($rows | map(
    . as $row
    | normalized_station_value($row.hfH; $row.hfHLv) as $norm
    | {
        timestamp: $row.nttimeter,
        raw_pollen: $norm.raw_pollen,
        display_value: $norm.display_value,
        numeric_value: $norm.numeric_value,
        level_code: $norm.level_code,
        level_text: $norm.level_text,
        advice: $row.advice,
        _warning: $norm.warning
      }
  )) as $series
| ($series[-1]) as $latest
| ($series[0]) as $earliest
| ($series | map(.numeric_value) | map(select(. != null))) as $numeric_values
| ($latest.numeric_value - $earliest.numeric_value) as $delta_24h
| {
    ok: true,
    mode: "history",
    generated_at: $generated_at,
    query: $query,
    data: {
      station: {
        station_id: ($rows[0].staId // null),
        station_name: ($rows[0].staName // null)
      },
      series: ($series | map(del(._warning))),
      summary: {
        latest_value: $latest.display_value,
        latest_level: {
          code: $latest.level_code,
          text: $latest.level_text
        },
        latest_advice: $latest.advice,
        min: (if ($numeric_values | length) == 0 then null else ($numeric_values | min) end),
        max: (if ($numeric_values | length) == 0 then null else ($numeric_values | max) end),
        delta_24h: (if ($latest.numeric_value == null or $earliest.numeric_value == null) then null else $delta_24h end),
        trend: (
          if ($latest.numeric_value == null or $earliest.numeric_value == null) then "unknown"
          elif $delta_24h > 10 then "rising"
          elif $delta_24h < -10 then "falling"
          else "steady"
          end
        )
      }
    },
    warnings: ($series | map(select(._warning != null) | ._warning))
  }
JQ

  jq -n \
    --argjson history "$history_json" \
    --argjson query "$query_json" \
    --arg generated_at "$generated_at" \
    "${JQ_COMMON_DEFS}${history_body}"
}

# ---------------------------------------------------------------------------
# Report mode builders
# ---------------------------------------------------------------------------

build_report_json() {
  local city_json="$1"
  local stations_json="$2"
  local history_json="$3"
  local generated_at="$4"
  local query_json="$5"
  local district_name="$6"

  local report_body
  read -r -d '' report_body <<'JQ' || true

($city.data.beijing // []) as $areas_raw
| ($stations.data // []) as $stations_raw
| ($history.data // []) as $history_rows

# Normalize areas
| ($areas_raw | map(
    . as $row
    | normalized_area("beijing_area"; $row.areaId; $row.name; $row.pollen) as $norm
    | {
        area_id: $row.areaId,
        name: $row.name,
        display_value: $norm.display_value,
        level_code: $norm.level_code,
        level_text: $norm.level_text,
        observed_at: $row.dataTime,
        _sort_value: $norm.sort_value,
        _warning: $norm.warning
      }
  )) as $areas

# Normalize stations
| ($stations_raw | map(
    . as $row
    | normalized_station("station"; $row.staId; $row.staName; $row.hfH; $row.hfHLv) as $norm
    | {
        station_id: $row.staId,
        station_name: $row.staName,
        display_value: $norm.display_value,
        level_code: $norm.level_code,
        level_text: $norm.level_text,
        observed_at: $row.nttimeter,
        advice: $row.advice,
        _sort_value: $norm.sort_value,
        _warning: $norm.warning
      }
  )) as $station_rows

# Target station (matched by district)
| ($station_rows | map(select(.station_name | contains($district_name))) | first) as $target

# History series
| ($history_rows | map(
    . as $row
    | normalized_station_value($row.hfH; $row.hfHLv) as $norm
    | {
        timestamp: $row.nttimeter,
        display_value: $norm.display_value,
        numeric_value: $norm.numeric_value,
        level_code: $norm.level_code,
        level_text: $norm.level_text,
        advice: $row.advice,
        _warning: $norm.warning
      }
  )) as $series
| ($series[-1]) as $latest_h
| ($series[0]) as $earliest_h
| ($series | map(.numeric_value) | map(select(. != null))) as $nums
| (if ($latest_h.numeric_value == null or $earliest_h.numeric_value == null) then null
   else ($latest_h.numeric_value - $earliest_h.numeric_value) end) as $delta

# City summary
| ($areas | map(.level_code) | map(select(. > 0))) as $valid_codes
| (if ($valid_codes | length) == 0 then 0
   else (($valid_codes | add) / ($valid_codes | length) | floor) end) as $avg_code

# Hotspots
| ($station_rows
    | sort_by([.level_code, ._sort_value]) | reverse | .[:$limit]
    | map({station_id, station_name, display_value, level_code, level_text})
  ) as $hotspots

# Alerts
| (
    ($areas | map(select(.level_code >= 4) | {source: "beijing_area", name, level_text, display_value}))
    + ($station_rows | map(select(.level_code >= 4) | {source: "station", name: .station_name, level_text, display_value}))
  ) as $alerts

# Warnings
| ($areas | map(select(._warning != null) | ._warning)) as $aw
| ($station_rows | map(select(._warning != null) | ._warning)) as $sw
| ($series | map(select(._warning != null) | ._warning)) as $hw

| {
    ok: true,
    mode: "report",
    generated_at: $generated_at,
    query: $query,
    data: {
      city_summary: {
        area_count: ($areas | length),
        avg_level_code: $avg_code,
        avg_level_text: level_text_from_code($avg_code),
        hotspots: $hotspots,
        alerts: $alerts
      },
      target_station: {
        station_id: $target.station_id,
        station_name: $target.station_name,
        current: {
          display_value: $target.display_value,
          level_code: $target.level_code,
          level_text: $target.level_text,
          observed_at: $target.observed_at,
          advice: $target.advice
        },
        trend_24h: {
          delta: $delta,
          direction: (
            if $delta == null then "unknown"
            elif $delta > 10 then "rising"
            elif $delta < -10 then "falling"
            else "steady"
            end
          ),
          min: (if ($nums | length) == 0 then null else ($nums | min) end),
          max: (if ($nums | length) == 0 then null else ($nums | max) end),
          series_points: ($series | length),
          latest_advice: $latest_h.advice
        }
      }
    },
    warnings: ($aw + $sw + $hw)
  }
JQ

  jq -n \
    --argjson city "$city_json" \
    --argjson stations "$stations_json" \
    --argjson history "$history_json" \
    --argjson query "$query_json" \
    --arg generated_at "$generated_at" \
    --argjson limit "$LIMIT" \
    --arg district_name "$district_name" \
    "${JQ_COMMON_DEFS}${report_body}"
}

build_report_text() {
  local city_json="$1"
  local stations_json="$2"
  local history_json="$3"
  local generated_at="$4"
  local query_json="$5"
  local district_name="$6"
  local cst_time="$7"

  local text_body
  read -r -d '' text_body <<'JQ' || true

($city.data.beijing // []) as $areas_raw
| ($stations.data // []) as $stations_raw
| ($history.data // []) as $history_rows

# Normalize areas
| ($areas_raw | map(
    . as $row
    | normalized_area("beijing_area"; $row.areaId; $row.name; $row.pollen) as $norm
    | { name: $row.name, display_value: $norm.display_value, level_code: $norm.level_code, level_text: $norm.level_text, _sort_value: $norm.sort_value }
  )) as $areas

# Normalize stations
| ($stations_raw | map(
    . as $row
    | normalized_station("station"; $row.staId; $row.staName; $row.hfH; $row.hfHLv) as $norm
    | {
        station_name: $row.staName,
        display_value: $norm.display_value, level_code: $norm.level_code, level_text: $norm.level_text,
        advice: $row.advice, _sort_value: $norm.sort_value
      }
  )) as $station_rows

# Target
| ($station_rows | map(select(.station_name | contains($district_name))) | first) as $target

# History
| ($history_rows | map(
    . as $row | normalized_station_value($row.hfH; $row.hfHLv) as $norm
    | { numeric_value: $norm.numeric_value, display_value: $norm.display_value, level_text: $norm.level_text, advice: $row.advice }
  )) as $series
| ($series[-1]) as $latest_h
| ($series[0]) as $earliest_h
| ($series | map(.numeric_value) | map(select(. != null))) as $nums
| (if ($latest_h.numeric_value == null or $earliest_h.numeric_value == null) then null
   else ($latest_h.numeric_value - $earliest_h.numeric_value) end) as $delta
| (if $delta == null then "未知"
   elif $delta > 10 then "上升"
   elif $delta < -10 then "下降"
   else "平稳" end) as $trend_text

# City avg
| ($areas | map(.level_code) | map(select(. > 0))) as $vc
| (if ($vc | length) == 0 then 0 else (($vc | add) / ($vc | length) | floor) end) as $avg_code

# Hotspots text
| ($station_rows | sort_by([.level_code, ._sort_value]) | reverse | .[:$limit]
    | map("\(.station_name) \(.display_value // "—")(\(.level_text))")
    | join(", ")
  ) as $hotspots_text

# Alerts count
| ([($areas | .[] | select(.level_code >= 4)), ($station_rows | .[] | select(.level_code >= 4))] | length) as $alert_count
| (if $alert_count == 0 then "无" else "\($alert_count) 项" end) as $alerts_text

# Build text
| "北京花粉日报（\($cst_time)）\n\n关注站点：\($target.station_name)\n当前：\($target.display_value // "—")（\($target.level_text)）\n24h趋势：\($trend_text)\(if $delta != null then "（\(if $delta >= 0 then "+" else "" end)\($delta | floor)）" else "" end)\(if ($nums | length) > 0 then "，范围 \($nums | min | floor)-\($nums | max | floor)" else "" end)\n建议：\($latest_h.advice // $target.advice // "暂无")\n\n全市概况：平均\(level_text_from_code($avg_code))\n热点：\($hotspots_text)\n预警：\($alerts_text)"

| {
    ok: true,
    mode: "report",
    format: "text",
    generated_at: $generated_at,
    query: $query,
    data: { text: . },
    warnings: []
  }
JQ

  jq -n \
    --argjson city "$city_json" \
    --argjson stations "$stations_json" \
    --argjson history "$history_json" \
    --argjson query "$query_json" \
    --arg generated_at "$generated_at" \
    --argjson limit "$LIMIT" \
    --arg district_name "$district_name" \
    --arg cst_time "$cst_time" \
    "${JQ_COMMON_DEFS}${text_body}"
}

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------

validate_common_arguments() {
  if ! is_positive_integer "$LIMIT"; then
    print_error_json "$EXIT_USAGE" "invalid_argument" "--limit must be a positive integer."
  fi

  if ! is_positive_integer "$TIMEOUT_MS"; then
    print_error_json "$EXIT_USAGE" "invalid_argument" "--timeout-ms must be a positive integer."
  fi

  case "$MODE" in
    overview|stations|history|report) ;;
    *)
      print_error_json "$EXIT_USAGE" "invalid_argument" "--mode must be one of: overview, stations, history, report."
      ;;
  esac

  if [[ "$MODE" == "history" && -z "$STATION_ID" && -z "$DISTRICT" ]]; then
    print_error_json "$EXIT_USAGE" "invalid_argument" "--district or --station-id is required when --mode history is used."
  fi

  if [[ "$MODE" == "report" && -z "$DISTRICT" ]]; then
    print_error_json "$EXIT_USAGE" "invalid_argument" "--district is required when --mode report is used."
  fi

  case "$FORMAT" in
    json|text) ;;
    *)
      print_error_json "$EXIT_USAGE" "invalid_argument" "--format must be one of: json, text."
      ;;
  esac
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
  if [[ $# -eq 0 ]]; then
    usage
    exit 0
  fi

  local command="$1"
  shift

  if [[ "$command" == "--help" || "$command" == "-h" || "$command" == "help" ]]; then
    usage
    exit 0
  fi

  if [[ "$command" != "query" ]]; then
    print_error_json "$EXIT_USAGE" "invalid_command" "Only the 'query' command is supported."
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --mode)
        [[ $# -ge 2 ]] || print_error_json "$EXIT_USAGE" "missing_argument" "--mode requires a value."
        MODE="$2"
        shift 2
        ;;
      --station-id)
        [[ $# -ge 2 ]] || print_error_json "$EXIT_USAGE" "missing_argument" "--station-id requires a value."
        STATION_ID="$2"
        shift 2
        ;;
      --district)
        [[ $# -ge 2 ]] || print_error_json "$EXIT_USAGE" "missing_argument" "--district requires a value."
        DISTRICT="$2"
        shift 2
        ;;
      --limit)
        [[ $# -ge 2 ]] || print_error_json "$EXIT_USAGE" "missing_argument" "--limit requires a value."
        LIMIT="$2"
        shift 2
        ;;
      --format)
        [[ $# -ge 2 ]] || print_error_json "$EXIT_USAGE" "missing_argument" "--format requires a value."
        FORMAT="$2"
        shift 2
        ;;
      --timeout-ms)
        [[ $# -ge 2 ]] || print_error_json "$EXIT_USAGE" "missing_argument" "--timeout-ms requires a value."
        TIMEOUT_MS="$2"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        print_error_json "$EXIT_USAGE" "invalid_argument" "Unknown argument: $1"
        ;;
    esac
  done

  require_command "curl" "Install curl with your system package manager if it is missing."
  require_command "jq" "Install jq with Homebrew (brew install jq) or your Linux package manager."

  validate_common_arguments

  local generated_at query_json city_json stations_json history_json
  generated_at="$(timestamp_utc)"
  query_json="$(query_object_json)"

  case "$MODE" in
    overview)
      city_json="$(fetch_json "$CITY_API")"
      validate_business_success "$city_json" "weatherPollen/pollens"
      if [[ "$(jq -r '(.data.beijing // []) | length' <<<"$city_json")" == "0" ]]; then
        print_error_json "$EXIT_EMPTY" "empty_data" "weatherPollen/pollens returned no Beijing area data."
      fi

      stations_json="$(fetch_json "$STATIONS_API")"
      validate_business_success "$stations_json" "pollen/obs/latestPollenLevels"
      if [[ "$(jq -r '(.data // []) | length' <<<"$stations_json")" == "0" ]]; then
        print_error_json "$EXIT_EMPTY" "empty_data" "latestPollenLevels returned no station data."
      fi

      build_overview_json "$city_json" "$stations_json" "$generated_at" "$query_json"
      ;;

    stations)
      stations_json="$(fetch_json "$STATIONS_API")"
      validate_business_success "$stations_json" "pollen/obs/latestPollenLevels"
      if [[ "$(jq -r '(.data // []) | length' <<<"$stations_json")" == "0" ]]; then
        print_error_json "$EXIT_EMPTY" "empty_data" "latestPollenLevels returned no station data."
      fi
      build_stations_json "$stations_json" "$generated_at" "$query_json"
      ;;

    history)
      # Resolve district to station ID if needed
      if [[ -n "$DISTRICT" && -z "$STATION_ID" ]]; then
        stations_json="$(fetch_json "$STATIONS_API")"
        validate_business_success "$stations_json" "pollen/obs/latestPollenLevels"
        STATION_ID="$(resolve_district_to_station_id "$stations_json" "$DISTRICT")"
        if [[ -z "$STATION_ID" || "$STATION_ID" == "null" ]]; then
          print_error_json "$EXIT_USAGE" "district_not_found" "No station found matching district: $DISTRICT. Available: 东城 西城 朝阳 海淀 丰台 石景山 门头沟 房山 通州 顺义 昌平 大兴 怀柔 平谷 密云 延庆"
        fi
      fi

      history_json="$(fetch_json "$BASE_URL/api/pollen/obs/history24?staId=$STATION_ID")"
      validate_business_success "$history_json" "pollen/obs/history24"
      if [[ "$(jq -r '(.data // []) | length' <<<"$history_json")" == "0" ]]; then
        print_error_json "$EXIT_EMPTY" "empty_data" "history24 returned no data for station id $STATION_ID."
      fi
      build_history_json "$history_json" "$generated_at" "$query_json"
      ;;

    report)
      city_json="$(fetch_json "$CITY_API")"
      validate_business_success "$city_json" "weatherPollen/pollens"

      stations_json="$(fetch_json "$STATIONS_API")"
      validate_business_success "$stations_json" "pollen/obs/latestPollenLevels"
      if [[ "$(jq -r '(.data // []) | length' <<<"$stations_json")" == "0" ]]; then
        print_error_json "$EXIT_EMPTY" "empty_data" "latestPollenLevels returned no station data."
      fi

      local target_station_id
      target_station_id="$(resolve_district_to_station_id "$stations_json" "$DISTRICT")"
      if [[ -z "$target_station_id" || "$target_station_id" == "null" ]]; then
        print_error_json "$EXIT_USAGE" "district_not_found" "No station found matching district: $DISTRICT. Available: 东城 西城 朝阳 海淀 丰台 石景山 门头沟 房山 通州 顺义 昌平 大兴 怀柔 平谷 密云 延庆"
      fi

      history_json="$(fetch_json "$BASE_URL/api/pollen/obs/history24?staId=$target_station_id")"
      validate_business_success "$history_json" "pollen/obs/history24"

      if [[ "$FORMAT" == "text" ]]; then
        local cst_time
        cst_time="$(timestamp_cst)"
        build_report_text "$city_json" "$stations_json" "$history_json" "$generated_at" "$query_json" "$DISTRICT" "$cst_time"
      else
        build_report_json "$city_json" "$stations_json" "$history_json" "$generated_at" "$query_json" "$DISTRICT"
      fi
      ;;
  esac
}

main "$@"
