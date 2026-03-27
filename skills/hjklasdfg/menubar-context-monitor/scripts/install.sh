#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}!${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
ask()   { echo -en "${YELLOW}?${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd || echo "$SCRIPT_DIR")"
PLUGIN_DIR="$HOME/Library/Application Support/SwiftBar/Plugins"
PLUGIN_NAME="context-monitor.30s.sh"
SSH_TARGET=""
FORCE_MODE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --remote) SSH_TARGET="$2"; FORCE_MODE="remote"; shift 2 ;;
    --local)  FORCE_MODE="local"; shift ;;
    *) echo "Usage: install.sh [--remote user@host] [--local]"; exit 1 ;;
  esac
done

echo ""
echo "🦞 Context Monitor — Installer"
echo "======================================="
echo ""

# --- Step 0: Check macOS ---
if [ "$(uname)" != "Darwin" ]; then
  error "This skill requires macOS (SwiftBar is macOS-only)."
  exit 1
fi

# --- Step 1: Detect environment ---
if [ "$FORCE_MODE" = "local" ]; then
  IS_HOST=true
  info "Forced local mode"
elif [ "$FORCE_MODE" = "remote" ]; then
  IS_HOST=false
  info "Remote mode → $SSH_TARGET"
elif [ -d "$HOME/.openclaw/agents" ]; then
  IS_HOST=true
  info "OpenClaw agents detected locally"
else
  IS_HOST=false
  warn "No local OpenClaw agents — assuming remote setup"
fi

# --- Step 2: Install SwiftBar ---
if [ -d "/Applications/SwiftBar.app" ]; then
  info "SwiftBar already installed"
else
  info "Installing SwiftBar via Homebrew..."
  if command -v brew &>/dev/null || [ -x /opt/homebrew/bin/brew ]; then
    BREW=$(command -v brew || echo /opt/homebrew/bin/brew)
    $BREW install --cask swiftbar
    info "SwiftBar installed"
  else
    error "Homebrew not found. Install SwiftBar manually."
    exit 1
  fi
fi

# --- Step 3: Create plugin directory ---
mkdir -p "$PLUGIN_DIR"

# --- Step 4: Determine mode ---
if [ "$IS_HOST" = true ]; then
  # Local mode: OpenClaw runs on this Mac
  info "Setting up LOCAL mode (OpenClaw on this machine)"
  
  # Install status collector
  cp "$SCRIPT_DIR/openclaw-status.py" "$HOME/.openclaw/openclaw-status.py"
  info "Status collector installed to ~/.openclaw/openclaw-status.py"
  
  # Install plugin (reuse swiftbar-plugin.sh with localhost as target)
  sed "s|MINI=\".*\"|MINI=\"localhost\"|" "$SCRIPT_DIR/swiftbar-plugin.sh" > "$PLUGIN_DIR/$PLUGIN_NAME"
  # For local mode, replace SSH call with direct python call
  sed -i '' 's|RAW=$(ssh $SSH_OPTS $MINI "python3 $STATUS_SCRIPT" 2>/dev/null)|RAW=$(python3 ~/.openclaw/openclaw-status.py 2>/dev/null)|' "$PLUGIN_DIR/$PLUGIN_NAME"
  chmod +x "$PLUGIN_DIR/$PLUGIN_NAME"
  info "Plugin installed (local mode)"
  
else
  # Remote mode: OpenClaw runs on another machine
  if [ -z "$SSH_TARGET" ]; then
    error "SSH target required. Usage: install.sh --remote user@host"
    exit 1
  fi
  
  # Test SSH connection
  echo ""
  warn "Testing SSH connection to $SSH_TARGET ..."
  if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$SSH_TARGET" "echo ok" &>/dev/null; then
    error "Cannot connect to $SSH_TARGET via SSH (passwordless)"
    echo ""
    echo "  Fix: Set up SSH key auth first:"
    echo "    ssh-keygen -t ed25519 -N ''"
    echo "    ssh-copy-id $SSH_TARGET"
    echo ""
    echo "  Then run this installer again."
    exit 1
  fi
  info "SSH connection OK"
  
  # Deploy status collector to remote host
  REMOTE_OPENCLAW=$(ssh -o BatchMode=yes "$SSH_TARGET" "echo \$HOME/.openclaw")
  scp -q "$SCRIPT_DIR/openclaw-status.py" "$SSH_TARGET:$REMOTE_OPENCLAW/openclaw-status.py"
  info "Status collector deployed to $SSH_TARGET:~/.openclaw/openclaw-status.py"
  
  # Install remote-mode plugin
  sed "s|MINI=\".*\"|MINI=\"$SSH_TARGET\"|" "$SCRIPT_DIR/swiftbar-plugin.sh" > "$PLUGIN_DIR/$PLUGIN_NAME"
  chmod +x "$PLUGIN_DIR/$PLUGIN_NAME"
  info "Plugin installed (remote mode → $SSH_TARGET)"
fi

# --- Step 5: Launch SwiftBar ---
if ! pgrep -x SwiftBar &>/dev/null; then
  open /Applications/SwiftBar.app
  info "SwiftBar launched"
  echo ""
  warn "First launch: SwiftBar may ask for plugin folder."
  warn "Select: ~/Library/Application Support/SwiftBar/Plugins"
else
  info "SwiftBar already running — plugin will refresh automatically"
fi

echo ""
echo "======================================="
echo "🦞 Done! Check your menu bar."
echo ""
echo "  Refresh interval: 30s (rename plugin file to change)"
echo "  Plugin: $PLUGIN_DIR/$PLUGIN_NAME"
echo ""
