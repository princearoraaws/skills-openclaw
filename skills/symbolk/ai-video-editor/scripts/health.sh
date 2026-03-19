#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="$HOME/.openclaw/config/sparki.env"
ERRORS=0

echo "=== Sparki Business API Health Check ==="
echo ""
echo "[Prerequisites]"
for cmd in python3 curl jq; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  OK  $cmd ($(command -v "$cmd"))"
  else
    echo "  FAIL $cmd not found"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
echo "[Configuration]"
if [ -f "$CONFIG_FILE" ]; then
  source "$CONFIG_FILE"
  if [ -n "${SPARKI_API_KEY:-}" ]; then
    echo "  OK  API key configured (${SPARKI_API_KEY:0:12}...)"
  else
    echo "  FAIL SPARKI_API_KEY not set in $CONFIG_FILE"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "  FAIL Config not found: $CONFIG_FILE"
  echo "       Run setup.sh first"
  ERRORS=$((ERRORS + 1))
fi

echo ""
echo "[API Connectivity]"
API_URL="${SPARKI_API_URL:-https://business-agent-api.sparki.io}"
if [ -n "${SPARKI_API_KEY:-}" ]; then
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/business/assets?page=1&page_size=1" \
    -H "X-API-Key: $SPARKI_API_KEY" 2>/dev/null || echo "000")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "  OK  Business API reachable and key valid ($API_URL)"
  else
    echo "  FAIL API returned HTTP $HTTP_CODE ($API_URL)"
    ERRORS=$((ERRORS + 1))
  fi
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "=== All checks passed ==="
else
  echo "=== $ERRORS check(s) failed ==="
  exit 1
fi
