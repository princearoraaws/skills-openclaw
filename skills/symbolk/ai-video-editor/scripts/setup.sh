#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.openclaw/config"
CONFIG_FILE="$CONFIG_DIR/sparki.env"

mkdir -p "$CONFIG_DIR"

echo "=== Sparki Business API Setup ==="

if [ ! -f "$CONFIG_FILE" ]; then
  cat > "$CONFIG_FILE" <<'EOF'
# Sparki Business API configuration
SPARKI_API_KEY=
SPARKI_API_URL=https://business-agent-api.sparki.io
SPARKI_OUTPUT_DIR=~/Movies/sparki
EOF
  chmod 600 "$CONFIG_FILE"
  echo "Created $CONFIG_FILE"
  echo "Fill in SPARKI_API_KEY, then run bash scripts/health.sh"
  exit 0
fi

chmod 600 "$CONFIG_FILE"
source "$CONFIG_FILE"

if [ -z "${SPARKI_API_KEY:-}" ]; then
  echo "WARN SPARKI_API_KEY is empty in $CONFIG_FILE"
  exit 1
fi

API_URL="${SPARKI_API_URL:-https://business-agent-api.sparki.io}"
echo "Verifying API key against $API_URL ..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/business/assets?page=1&page_size=1" \
  -H "X-API-Key: $SPARKI_API_KEY" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
  echo "API key verification passed"
else
  echo "API key verification failed: HTTP $HTTP_CODE"
  exit 1
fi

OUTPUT_DIR="${SPARKI_OUTPUT_DIR:-$HOME/Movies/sparki}"
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"
mkdir -p "$OUTPUT_DIR"
echo "Output directory ready: $OUTPUT_DIR"
