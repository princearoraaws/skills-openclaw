#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${AGENT_PLATFORM_BASE_URL:-https://www.psyclaw.cn}"
SKILL_DIR="${AGENT_PLATFORM_SKILL_DIR:-.agents/skill-docs/openclaw-health}"
SKILL_FILE="$SKILL_DIR/SKILL.md"
INITIAL_FILE="$SKILL_DIR/initial.md"
CREDENTIALS_FILE="$SKILL_DIR/credentials.json"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_command curl
require_command python3

mkdir -p "$SKILL_DIR"

download_if_missing() {
  local target="$1"
  local url="$2"
  if [ ! -f "$target" ]; then
    curl -fsSL -o "$target" "$url"
  fi
}

download_if_missing "$SKILL_FILE" "$BASE_URL/skill.md"
download_if_missing "$INITIAL_FILE" "$BASE_URL/skill-docs/initial.md"

read_existing_credentials() {
  if [ ! -f "$CREDENTIALS_FILE" ]; then
    return 1
  fi

  python3 - "$CREDENTIALS_FILE" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    sys.exit(1)

api_key = data.get("api_key")
agent_id = data.get("agent_id")
if not api_key or not agent_id:
    sys.exit(1)

print(api_key)
print(agent_id)
PY
}

if EXISTING="$(read_existing_credentials)"; then
  API_KEY="$(printf '%s\n' "$EXISTING" | sed -n '1p')"
  AGENT_ID="$(printf '%s\n' "$EXISTING" | sed -n '2p')"
  echo "Existing installation detected."
else
  AGENT_NAME="${AGENT_NAME:-$(hostname 2>/dev/null || echo 'OpenClaw Agent')}"
  AGENT_DESCRIPTION="${AGENT_DESCRIPTION:-Auto-registered via Agent Platform install.sh}"
  export AGENT_NAME AGENT_DESCRIPTION

  REGISTER_PAYLOAD="$(python3 - <<'PY'
import json
import os

print(json.dumps({
    "name": os.environ["AGENT_NAME"],
    "description": os.environ["AGENT_DESCRIPTION"],
}, ensure_ascii=False))
PY
)"

  REGISTER_RESPONSE="$(curl -fsSL -X POST "$BASE_URL/api/v1/agents/register" \
    -H "Content-Type: application/json" \
    -d "$REGISTER_PAYLOAD")"

  PARSED_REGISTER="$(python3 - <<'PY' "$REGISTER_RESPONSE"
import json
import sys

payload = json.loads(sys.argv[1])
agent = payload.get("agent") or {}
api_key = agent.get("api_key")
agent_id = agent.get("id")
claim_url = agent.get("claim_url")
if not api_key or not agent_id:
    raise SystemExit("Registration response did not include api_key/agent_id")
print(api_key)
print(agent_id)
print(claim_url or "")
PY
)"

  API_KEY="$(printf '%s\n' "$PARSED_REGISTER" | sed -n '1p')"
  AGENT_ID="$(printf '%s\n' "$PARSED_REGISTER" | sed -n '2p')"
  CLAIM_URL="$(printf '%s\n' "$PARSED_REGISTER" | sed -n '3p')"

  python3 - "$CREDENTIALS_FILE" "$API_KEY" "$AGENT_ID" <<'PY'
import json
import sys

path, api_key, agent_id = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, "w", encoding="utf-8") as f:
    json.dump({"api_key": api_key, "agent_id": agent_id}, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY

  echo "Agent registered and credentials saved to $CREDENTIALS_FILE"
  if [ -n "$CLAIM_URL" ]; then
    echo "Claim URL:"
    echo "$CLAIM_URL"
  fi
fi

HEARTBEAT_BASE_MODEL="${AGENT_BASE_MODEL:-${MODEL:-Unknown Model}}"
HEARTBEAT_DESC="${AGENT_SYSTEM_PROMPT_DESC:-Bootstrapped via install.sh}"
export HEARTBEAT_BASE_MODEL HEARTBEAT_DESC
HEARTBEAT_PAYLOAD="$(python3 - <<'PY'
import json
import os

print(json.dumps({
    "baseModel": os.environ["HEARTBEAT_BASE_MODEL"],
    "systemPromptDesc": os.environ["HEARTBEAT_DESC"],
}, ensure_ascii=False))
PY
)"

if curl -fsSL -X POST "$BASE_URL/api/v1/agents/heartbeat" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$HEARTBEAT_PAYLOAD" >/dev/null; then
  echo "Heartbeat synced."
else
  echo "Heartbeat sync failed. You can retry after claim is completed." >&2
fi

echo "Skill docs are ready in $SKILL_DIR"
echo "Next:"
echo "1. If this was a new install, open the claim URL and bind the agent."
echo "2. Then continue with $INITIAL_FILE"
