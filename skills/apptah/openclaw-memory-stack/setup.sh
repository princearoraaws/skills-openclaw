#!/usr/bin/env bash
# OpenClaw Memory Stack — Setup Script
# Validates license key and registers as OpenClaw memory provider.
#
# Usage:
#   ./setup.sh --key=oc-starter-xxxxxxxxxxxx
#
# Prerequisites: bash, curl, OpenClaw 2026.3.2+
# Optional: bun (for QMD vector search backend)
set -euo pipefail

INSTALL_ROOT="$HOME/.openclaw/memory-stack"
STATE_DIR="$HOME/.openclaw/state"
ACTIVATE_URL="https://openclaw-license.busihoward.workers.dev/api/activate"

if [[ -t 1 ]]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; NC='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; NC=''
fi

info()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!!]${NC} $1"; }
fail()  { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

LICENSE_KEY=""
for arg in "$@"; do
  case "$arg" in
    --key=*) LICENSE_KEY="${arg#--key=}" ;;
    --help|-h)
      echo "Usage: setup.sh --key=oc-starter-xxxxxxxxxxxx"
      echo ""
      echo "Validates your license key and registers Memory Stack"
      echo "as the active memory provider for OpenClaw."
      echo ""
      echo "After setup, restart OpenClaw to activate:"
      echo "  openclaw gateway restart"
      exit 0
      ;;
  esac
done

[[ -z "$LICENSE_KEY" ]] && fail "Missing --key flag. Usage: setup.sh --key=oc-starter-xxxxxxxxxxxx"

command -v curl &>/dev/null || fail "curl is required but not found."

if command -v bun &>/dev/null; then
  info "Bun found — QMD vector search backend available"
else
  warn "Bun not found — QMD vector search disabled. Install: https://bun.sh"
fi

echo "Validating license key..."
DEVICE_ID=$(hostname | shasum -a 256 | cut -c1-16)

RESPONSE=$(curl -sf -X POST "$ACTIVATE_URL" \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"$LICENSE_KEY\",\"device_id\":\"$DEVICE_ID\"}" 2>/dev/null) \
  || fail "License validation failed. Check your key or network."

if echo "$RESPONSE" | grep -q '"activated":true\|"status":"active"\|"valid":true'; then
  info "License verified"
else
  fail "Invalid license key. Purchase at: https://openclaw-memory.apptah.com"
fi

mkdir -p "$INSTALL_ROOT" "$STATE_DIR"

echo "$LICENSE_KEY" > "$STATE_DIR/license.key"
chmod 600 "$STATE_DIR/license.key"
info "License saved"

OPENCLAW_CONFIG="$HOME/.openclaw/settings.json"
if [[ -f "$OPENCLAW_CONFIG" ]]; then
  if grep -q "memory-stack" "$OPENCLAW_CONFIG" 2>/dev/null; then
    info "Already registered as OpenClaw memory provider"
  else
    warn "Add memory-stack to your OpenClaw settings manually:"
    echo "  Edit $OPENCLAW_CONFIG and add to 'memory.providers':"
    echo '  { "name": "memory-stack", "path": "~/.openclaw/memory-stack" }'
  fi
else
  warn "OpenClaw config not found at $OPENCLAW_CONFIG"
  echo "  Install OpenClaw first: https://openclaw.ai"
fi

echo ""
info "Memory Stack setup complete!"
echo ""
echo "Next steps:"
echo "  1. Restart OpenClaw:         openclaw gateway restart"
echo "  2. Initialize a project:     openclaw-memory init ."
echo "  3. Enable vector search:     openclaw-memory embed"
echo "  4. Check engine health:      openclaw-memory health"
echo "  5. Start searching:          openclaw-memory \"your query\""
