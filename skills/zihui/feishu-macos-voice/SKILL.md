---
name: feishu-voice
description: Send voice/audio messages to Feishu (Lark) chats using macOS TTS. Converts text to speech via macOS `say` command, transcodes to opus format with ffmpeg, uploads to Feishu Open API, and delivers as a native audio message. Use when asked to "send a voice message", "发语音", "用语音说", or any request to send audio to Feishu/Lark. Requires macOS + ffmpeg + Feishu bot credentials.
---

# Feishu Voice Message

Send voice messages to Feishu (Lark) via TTS → opus → Feishu API.

## Prerequisites

- macOS (uses `say` command for TTS)
- `ffmpeg` with libopus: `brew install ffmpeg`
- Feishu bot `app_id` + `app_secret` — read from `~/.openclaw/openclaw.json` → `channels.feishu`

## Quick Send

Use the bundled script for one-shot sending:

```bash
scripts/feishu-voice.sh "你好，谢欣！" <open_id_or_chat_id> [open_id|chat_id] [voice]
```

Examples:
```bash
# Send to a user (open_id)
scripts/feishu-voice.sh "今天天气不错！" ou_xxxxxxxx open_id Tingting

# Send to a group (chat_id)
scripts/feishu-voice.sh "会议提醒" oc_xxxxxxxx chat_id Tingting
```

## Manual Step-by-Step

### 1. Get credentials

```bash
APP_ID=$(python3 -c "import json; d=json.load(open('$HOME/.openclaw/openclaw.json')); print(d['channels']['feishu']['appId'])")
APP_SECRET=$(python3 -c "import json; d=json.load(open('$HOME/.openclaw/openclaw.json')); print(d['channels']['feishu']['appSecret'])")
```

### 2. TTS → AIFF

```bash
say -v "Tingting" "要说的文字" -o /tmp/voice.aiff
```

### 3. Transcode to opus ⚠️ All three flags required

```bash
ffmpeg -y -i /tmp/voice.aiff -acodec libopus -ac 1 -ar 16000 /tmp/voice.opus
```

| Flag | Value | Why |
|------|-------|-----|
| `-acodec libopus` | opus codec | Feishu only accepts opus |
| `-ac 1` | mono | Required by Feishu |
| `-ar 16000` | 16 kHz | Required by Feishu |

### 4. Get duration in **milliseconds**

```bash
DURATION_MS=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 /tmp/voice.opus \
  | python3 -c "import sys; print(round(float(sys.stdin.read().strip()) * 1000))")
```

⚠️ `duration` param is **milliseconds**, not seconds. Wrong unit → 0s display.

### 5. Get tenant_access_token

```bash
TENANT_TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")
```

### 6. Upload file

```bash
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.opus" \
  -F "duration=$DURATION_MS" \
  -F "file=@/tmp/voice.opus" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['file_key'])")
```

⚠️ `file_type` must be `opus`, **not** `audio`.

### 7. Send audio message

```bash
# To a user (open_id)
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}"

# To a group, change receive_id_type=chat_id and use oc_xxx
```

## Voice Options (Chinese)

| Voice | Language | Notes |
|-------|----------|-------|
| `Tingting` | 普通话 zh_CN | Recommended default |
| `Meijia` | 台湾 zh_TW | |
| `Sinji` | 粤语 zh_HK | |

List all available: `say -v '?'`

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Duration shows 0s | `duration` unit is seconds, not ms | Multiply by 1000 |
| Upload fails 400 | `file_type=audio` used | Change to `opus` |
| Silent/tiny AIFF | Voice pack not installed | System Settings → Accessibility → Spoken Content → download voice |
| Garbled audio | Missing `-ac 1 -ar 16000` | Add both ffmpeg flags |
