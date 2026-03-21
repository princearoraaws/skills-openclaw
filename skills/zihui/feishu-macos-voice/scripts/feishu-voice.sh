#!/usr/bin/env bash
# feishu-voice.sh — Send a voice message to Feishu via TTS
#
# Usage:
#   feishu-voice.sh <text> <receive_id> [receive_id_type] [voice]
#
# Args:
#   text             Text to speak
#   receive_id       open_id (ou_xxx) or chat_id (oc_xxx)
#   receive_id_type  "open_id" or "chat_id" (default: auto-detect by prefix)
#   voice            macOS TTS voice name (default: Tingting)
#
# Requires: ffmpeg, jq (optional), Feishu bot credentials in ~/.openclaw/openclaw.json

set -euo pipefail

TEXT="${1:-}"
RECEIVE_ID="${2:-}"
RECEIVE_ID_TYPE="${3:-}"
VOICE="${4:-Tingting}"
TMP_AIFF="/tmp/feishu-voice-$$.aiff"
TMP_OPUS="/tmp/feishu-voice-$$.opus"

# --- Validate args ---
if [[ -z "$TEXT" || -z "$RECEIVE_ID" ]]; then
  echo "Usage: $0 <text> <receive_id> [open_id|chat_id] [voice]" >&2
  exit 1
fi

# Auto-detect receive_id_type if not specified
if [[ -z "$RECEIVE_ID_TYPE" ]]; then
  if [[ "$RECEIVE_ID" == oc_* ]]; then
    RECEIVE_ID_TYPE="chat_id"
  else
    RECEIVE_ID_TYPE="open_id"
  fi
fi

# --- Read credentials from openclaw config ---
CONFIG="$HOME/.openclaw/openclaw.json"
APP_ID=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['channels']['feishu']['appId'])")
APP_SECRET=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d['channels']['feishu']['appSecret'])")

if [[ -z "$APP_ID" || -z "$APP_SECRET" ]]; then
  echo "Error: Could not read Feishu credentials from $CONFIG" >&2
  exit 1
fi

echo "🎙️  TTS: voice=$VOICE"

# --- Step 1: TTS → AIFF ---
say -v "$VOICE" "$TEXT" -o "$TMP_AIFF"

# --- Step 2: Transcode to opus (mono, 16kHz — required by Feishu) ---
ffmpeg -y -i "$TMP_AIFF" -acodec libopus -ac 1 -ar 16000 "$TMP_OPUS" 2>/dev/null
echo "🔄  Transcoded to opus"

# --- Step 3: Duration in milliseconds ---
DURATION_MS=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$TMP_OPUS" \
  | python3 -c "import sys; print(round(float(sys.stdin.read().strip()) * 1000))")
echo "⏱️  Duration: ${DURATION_MS}ms"

# --- Step 4: Get tenant_access_token ---
TENANT_TOKEN=$(curl -sf -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# --- Step 5: Upload file ---
FILE_KEY=$(curl -sf -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.opus" \
  -F "duration=$DURATION_MS" \
  -F "file=@$TMP_OPUS" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['file_key'])")
echo "☁️  Uploaded: $FILE_KEY"

# --- Step 6: Send audio message ---
RESULT=$(curl -sf -X POST \
  "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=$RECEIVE_ID_TYPE" \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}") 

MSG_ID=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['message_id'] if d['code']==0 else 'ERROR: '+d['msg'])")
echo "✅  Sent: $MSG_ID"

# Cleanup
rm -f "$TMP_AIFF" "$TMP_OPUS"
