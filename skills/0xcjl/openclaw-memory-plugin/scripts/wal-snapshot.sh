#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# wal-snapshot.sh — Write-Ahead Log snapshot trigger for OpenClaw memory
#
# Call this on significant memory writes (after-task hook, manual saves, etc.)
# to ensure indexes stay fresh without blocking the write path.
#
# Usage:
#   ./wal-snapshot.sh rebuild     # Full index rebuild (indexer + BM25)
#   ./wal-snapshot.sh status       # Show last build timestamp
#   ./wal-snapshot.sh index-only   # Only rebuild keyword index (faster)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

AGENT_ID="${AGENT_ID:-dev}"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$HOME/.openclaw/workspace-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEXER="$SCRIPT_DIR/memory-indexer.py"
BM25="$SCRIPT_DIR/bm25_search.py"
STATE_FILE="$WORKSPACE_ROOT/.memory_wal_state"

log()  { echo "[wal-snapshot] $*"; }
err()  { echo "[wal-snapshot] ERROR: $*" >&2; }

# ─── Status ──────────────────────────────────────────────────────────────────
cmd_status() {
  if [[ -f "$STATE_FILE" ]]; then
    cat "$STATE_FILE"
  else
    echo "last_build: never (no WAL snapshot run yet)"
  fi
}

# ─── Index-only (fast) ────────────────────────────────────────────────────────
cmd_index_only() {
  python3 -c "
import time, subprocess, sys
from datetime import datetime

start = time.perf_counter()
r = subprocess.run(['python3', '$INDEXER', 'build', '--agent-id', '$AGENT_ID'],
                  capture_output=True, text=True)
elapsed = (time.perf_counter() - start) * 1000
print('[wal-snapshot] Keyword index done in {:.0f}ms'.format(elapsed), file=sys.stderr)
with open('$STATE_FILE', 'w') as f:
    f.write('last_build: ' + datetime.now().isoformat() + '\n')
" 2>&1
}

# ─── Full rebuild ─────────────────────────────────────────────────────────────
cmd_rebuild() {
  python3 -c "
import time, subprocess, sys

start_total = time.perf_counter()

# Keyword index
start_idx = time.perf_counter()
r1 = subprocess.run(['python3', '$INDEXER', 'build', '--agent-id', '$AGENT_ID'],
                   capture_output=True, text=True)
elapsed_idx = (time.perf_counter() - start_idx) * 1000
print('[wal-snapshot] Keyword index done in {:.0f}ms'.format(elapsed_idx))
if r1.stderr:
    print('  indexer:', r1.stderr.strip()[:200], file=sys.stderr)

# BM25 index
start_bm = time.perf_counter()
r2 = subprocess.run(['python3', '$BM25', '--build', '--agent-id', '$AGENT_ID'],
                   capture_output=True, text=True)
elapsed_bm = (time.perf_counter() - start_bm) * 1000
print('[wal-snapshot] BM25 done in {:.0f}ms'.format(elapsed_bm))

total = (time.perf_counter() - start_total) * 1000
print('[wal-snapshot] Total WAL snapshot: {:.0f}ms'.format(total))

with open('$STATE_FILE', 'w') as f:
    from datetime import datetime
    f.write('last_build: ' + datetime.now().isoformat() + '\n')
" 2>&1
}

# ─── CLI ─────────────────────────────────────────────────────────────────────
CMD="${1:-rebuild}"
case "$CMD" in
  rebuild|build)   cmd_rebuild ;;
  index-only)      cmd_index_only ;;
  status)          cmd_status ;;
  *)               err "Unknown command: $CMD" && exit 1 ;;
esac
