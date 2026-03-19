#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="$HOME/.openclaw/config/sparki.env"
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE"

API_URL="${SPARKI_API_URL:-https://business-agent-api.sparki.io}"
API_KEY="${SPARKI_API_KEY:?ERROR: SPARKI_API_KEY not set. Run setup.sh or edit $CONFIG_FILE}"
OUTPUT_DIR="${SPARKI_OUTPUT_DIR:-$HOME/Movies/sparki}"
BUSINESS_API_BASE="$API_URL/api/v1/business"
ASSET_POLL_INTERVAL="${ASSET_POLL_INTERVAL:-2}"
ASSET_POLL_MAX_INTERVAL="${ASSET_POLL_MAX_INTERVAL:-30}"
PROJECT_POLL_INTERVAL="${PROJECT_POLL_INTERVAL:-10}"
PROJECT_POLL_MAX_INTERVAL="${PROJECT_POLL_MAX_INTERVAL:-60}"
ASSET_TIMEOUT="${ASSET_TIMEOUT:-300}"
PROJECT_TIMEOUT="${PROJECT_TIMEOUT:-3600}"

VIDEO_PATH="${1:?Usage: edit_video.sh <video_path> <tips> [user_prompt] [aspect_ratio] [duration]}"
TIPS_ARG="${2:-}"
USER_PROMPT="${3:-}"
ASPECT_RATIO="${4:-9:16}"
DURATION="${5:-}"

VIDEO_PATH="${VIDEO_PATH/#\~/$HOME}"
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"

if [ ! -f "$VIDEO_PATH" ]; then
  echo "ERROR: Video file not found: $VIDEO_PATH"
  exit 1
fi

case "${VIDEO_PATH##*.}" in
  mp4|MP4) ;;
  *)
    echo "ERROR: Only MP4 is supported by this documented Business API"
    exit 1
    ;;
esac

if [ -z "$TIPS_ARG" ] && [ ${#USER_PROMPT} -lt 10 ]; then
  echo "ERROR: When tips is empty, user_prompt must be at least 10 characters"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

calculate_backoff_seconds() {
  local attempt="$1"
  local initial_interval="$2"
  local max_interval="$3"
  local delay="$initial_interval"

  if [ "$attempt" -le 0 ]; then
    echo "$delay"
    return
  fi

  while [ "$attempt" -gt 0 ]; do
    if [ "$delay" -ge "$max_interval" ]; then
      echo "$max_interval"
      return
    fi

    delay=$((delay * 2))
    if [ "$delay" -gt "$max_interval" ]; then
      delay="$max_interval"
    fi
    attempt=$((attempt - 1))
  done

  echo "$delay"
}

echo "=== Sparki AI Video Editor ==="
echo "Video: $VIDEO_PATH"
echo "Tips: ${TIPS_ARG:-<empty>}"
echo "Prompt: ${USER_PROMPT:-<empty>}"
echo "Aspect Ratio: $ASPECT_RATIO"
echo "Duration: ${DURATION:-<empty>}"
echo "API: $API_URL"
echo ""

echo "[1/4] Uploading asset..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BUSINESS_API_BASE/assets/upload" \
  -H "X-API-Key: $API_KEY" \
  -F "files=@$VIDEO_PATH")

OBJECT_KEY=$(echo "$UPLOAD_RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    uploads = ((data.get("data") or {}).get("uploads") or [])
    first = uploads[0] if uploads else {}
    print(first.get("object_key", ""))
except Exception:
    print("")
' 2>/dev/null)

if [ -z "$OBJECT_KEY" ]; then
  echo "ERROR: Upload failed: $UPLOAD_RESPONSE"
  exit 1
fi

echo "  Uploaded object_key: $OBJECT_KEY"

echo "[2/4] Waiting for asset processing..."
ASSET_START=$(date +%s)
ASSET_ATTEMPT=0
while true; do
  ASSET_BATCH_PAYLOAD=$(python3 -c '
import json, sys
print(json.dumps({"object_keys": [sys.argv[1]]}))
' "$OBJECT_KEY")

  ASSET_BATCH_RESPONSE=$(curl -s -X POST "$BUSINESS_API_BASE/assets/batch" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$ASSET_BATCH_PAYLOAD")

  ASSET_STATUS=$(echo "$ASSET_BATCH_RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    assets = ((data.get("data") or {}).get("assets") or [])
    first = assets[0] if assets else {}
    print(first.get("status", "unknown"))
except Exception:
    print("unknown")
' 2>/dev/null || echo "unknown")

  echo "  Asset status: $ASSET_STATUS"

  if [ "$ASSET_STATUS" = "completed" ]; then
    break
  fi
  if [ "$ASSET_STATUS" = "failed" ] || [ "$ASSET_STATUS" = "error" ]; then
    echo "ERROR: Asset processing failed: $ASSET_BATCH_RESPONSE"
    exit 1
  fi

  NOW=$(date +%s)
  if [ $((NOW - ASSET_START)) -ge "$ASSET_TIMEOUT" ]; then
    echo "ERROR: Asset processing timed out after ${ASSET_TIMEOUT}s"
    exit 1
  fi

  ASSET_DELAY=$(calculate_backoff_seconds "$ASSET_ATTEMPT" "$ASSET_POLL_INTERVAL" "$ASSET_POLL_MAX_INTERVAL")
  echo "  Retrying asset status in ${ASSET_DELAY}s..."
  sleep "$ASSET_DELAY"
  ASSET_ATTEMPT=$((ASSET_ATTEMPT + 1))
done

echo "[3/4] Creating render project..."
PROJECT_PAYLOAD=$(python3 -c '
import json, sys

def parse_tips(raw: str):
    values = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(int(item) if item.isdigit() else item)
    return values

object_key, tips_arg, user_prompt, aspect_ratio, duration = sys.argv[1:6]
payload = {
    "object_keys": [object_key],
    "aspect_ratio": aspect_ratio or "9:16",
}

tips = parse_tips(tips_arg)
if tips:
    payload["tips"] = tips
if user_prompt:
    payload["user_prompt"] = user_prompt
if duration:
    payload["duration"] = int(duration)

print(json.dumps(payload))
' "$OBJECT_KEY" "$TIPS_ARG" "$USER_PROMPT" "$ASPECT_RATIO" "$DURATION")

PROJECT_RESPONSE=$(curl -s -X POST "$BUSINESS_API_BASE/projects/render" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PROJECT_PAYLOAD")

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    print(((data.get("data") or {}).get("project_id", "")))
except Exception:
    print("")
' 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
  echo "ERROR: Project creation failed: $PROJECT_RESPONSE"
  exit 1
fi

echo "  Project ID: $PROJECT_ID"

echo "[4/4] Waiting for render completion..."
PROJECT_START=$(date +%s)
PROJECT_ATTEMPT=0
while true; do
  PROJECT_BATCH_PAYLOAD=$(python3 -c '
import json, sys
print(json.dumps({"project_ids": [sys.argv[1]]}))
' "$PROJECT_ID")

  PROJECT_BATCH_RESPONSE=$(curl -s -X POST "$BUSINESS_API_BASE/projects/batch" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$PROJECT_BATCH_PAYLOAD")

  PROJECT_STATUS=$(echo "$PROJECT_BATCH_RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    projects = ((data.get("data") or {}).get("projects") or [])
    first = projects[0] if projects else {}
    print(first.get("status", "unknown"))
except Exception:
    print("unknown")
' 2>/dev/null || echo "unknown")

  echo "  Project status: $PROJECT_STATUS"

  if [ "$PROJECT_STATUS" = "completed" ]; then
    break
  fi
  if [ "$PROJECT_STATUS" = "failed" ] || [ "$PROJECT_STATUS" = "error" ]; then
    echo "ERROR: Project failed: $PROJECT_BATCH_RESPONSE"
    exit 1
  fi

  NOW=$(date +%s)
  if [ $((NOW - PROJECT_START)) -ge "$PROJECT_TIMEOUT" ]; then
    echo "ERROR: Project processing timed out after ${PROJECT_TIMEOUT}s"
    exit 1
  fi

  PROJECT_DELAY=$(calculate_backoff_seconds "$PROJECT_ATTEMPT" "$PROJECT_POLL_INTERVAL" "$PROJECT_POLL_MAX_INTERVAL")
  echo "  Retrying project status in ${PROJECT_DELAY}s..."
  sleep "$PROJECT_DELAY"
  PROJECT_ATTEMPT=$((PROJECT_ATTEMPT + 1))
done

RESULT_URL=$(echo "$PROJECT_BATCH_RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    projects = ((data.get("data") or {}).get("projects") or [])
    project = projects[0] if projects else {}
    videos = project.get("output_videos") or []
    first = videos[0] if videos else {}
    print(first.get("url", ""))
except Exception:
    print("")
' 2>/dev/null)

if [ -z "$RESULT_URL" ]; then
  echo "ERROR: Missing output video URL: $PROJECT_BATCH_RESPONSE"
  exit 1
fi

OUTPUT_FILE="$OUTPUT_DIR/${PROJECT_ID}.mp4"
curl -s -L -o "$OUTPUT_FILE" "$RESULT_URL"

if [ ! -f "$OUTPUT_FILE" ]; then
  echo "ERROR: Download failed"
  exit 1
fi

FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
echo ""
echo "=== Done! ==="
echo "Output: $OUTPUT_FILE ($FILE_SIZE)"
