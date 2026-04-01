#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# memory-hook.sh — Session lifecycle hooks for OpenClaw multi-agent memory
#
# Hooks:
#   before-task  — run before agent starts a new task (recall)
#   after-task   — run after agent completes a task (save)
#   dag-link     — link a memory entry into the DAG
#   build        — rebuild all indexes
#   search       — CLI search wrapper
#
# Env vars:
#   AGENT_ID       — current agent name (default: dev)
#   WORKSPACE_ROOT — root of openclaw workspace
#
# Performance target: recall < 500ms
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

AGENT_ID="${AGENT_ID:-dev}"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$HOME/.openclaw/workspace-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEXER="$SCRIPT_DIR/memory-indexer.py"
BM25="$SCRIPT_DIR/bm25_search.py"
WAL_SNAPSHOT="$SCRIPT_DIR/wal-snapshot.sh"
MEMORY_DIR="$WORKSPACE_ROOT/memory"
INDEX_FILE="$MEMORY_DIR/index.json"
BM25_INDEX_FILE="$MEMORY_DIR/bm25_index.json"

YELLOW='\033[1;33m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${YELLOW}[memory-hook]${NC} $*"; }
ok()   { echo -e "${GREEN}[memory-hook]${NC} $*"; }
err()  { echo -e "${RED}[memory-hook] ERROR:${NC} $*" >&2; }

usage() {
  cat <<EOF
Usage: memory-hook.sh <mode> [options]

Modes:
  before-task <task_description>
    Recall relevant memories before starting a task.
  after-task <task_description> [result_file]
    Save task output to memory/ after completion.
  dag-link <memory_id> <linked_id> [reason]
    Record a DAG link between two memory entries.
  build
    Rebuild all indexes.
  search <query>
    CLI search wrapper.

Examples:
  memory-hook.sh before-task "优化 Vue 性能"
  memory-hook.sh after-task "完成 Vue 优化" /tmp/result.md
  memory-hook.sh dag-link abc123 def456 "基于前者的架构"
  memory-hook.sh build
  memory-hook.sh search "BM25 实现"
EOF
}

# ─── before-task ─────────────────────────────────────────────────────────────
hook_before_task() {
  local task="$1"
  log "before-task recall: ${task:0:60}"

  local recall_output elapsed_ms
  # FIX: Pass args via argv (no shell injection risk).
  # Previously used embedded variables in python -c string (shell injection).
  recall_output=$(python3 -c "
import sys, time, subprocess, json

start = time.perf_counter()
args = sys.argv[1:]
if not args:
    sys.exit(1)
task_s = args[0]
agent_s = args[1]
bm25_exe = args[2]
idx_exe = args[3]

try:
    r = subprocess.run(['python3', bm25_exe, '--search', task_s, '--agent-id', agent_s, '--top', '3', '--json'],
                      capture_output=True, timeout=3)
    if r.returncode == 0 and r.stdout.strip():
        data = json.loads(r.stdout)
        if data:
            sys.stdout.write(r.stdout)
            sys.exit(0)
except Exception as e:
    sys.stderr.write(str(e) + '\n')

try:
    r = subprocess.run(['python3', idx_exe, '--search', task_s, '--agent-id', agent_s, '--top', '3', '--json'],
                      capture_output=True, timeout=3)
    if r.returncode == 0 and r.stdout.strip():
        sys.stdout.write(r.stdout)
except Exception as e:
    sys.stderr.write(str(e) + '\n')

elapsed_ms = (time.perf_counter() - start) * 1000
sys.stderr.write('HOOK_ELAPSED:' + str(int(elapsed_ms)) + 'ms\n')
" "$task" "$AGENT_ID" "$BM25" "$INDEXER" 2>&1) || true

  echo ""
  echo "## 记忆召回 (before-task)"
  echo ""
  echo "任务: $task"
  echo ""

  # Extract elapsed time from stderr
  elapsed_ms=$(echo "$recall_output" | grep "HOOK_ELAPSED:" | sed 's/.*HOOK_ELAPSED://') || elapsed_ms=""

  # Extract JSON output (exclude log lines and HOOK_ELAPSED)
  local json_output
  json_output=$(echo "$recall_output" | grep -v "HOOK_ELAPSED:" | grep -v "^\[memory" | grep -v "^\[" | grep -v "^  " | grep -v "^---" | grep "^$" || true)

  if echo "$recall_output" | grep -q "^\[.*$"; then
    # Found log line prefix, extract the JSON block
    json_output=$(echo "$recall_output" | grep -v "HOOK_ELAPSED:")
    # Check if it starts with [ (JSON array)
    if [[ "$json_output" == \[* ]]; then
      echo "$json_output" | python3 -c "
import json, sys
try:
    results = json.load(sys.stdin)
    print('### 相关记忆 (top 3):')
    print()
    for i, r in enumerate(results, 1):
        shared_tag = ' [shared]' if r.get('shared') else ''
        print(str(i) + '. ' + r['file'] + shared_tag)
        print('   ' + r.get('summary', '')[:120])
        print()
except Exception as e:
    sys.stderr.write(str(e) + '\n')
" 2>/dev/null
    fi
  elif [[ -n "$json_output" ]] && [[ "$json_output" == \[* ]]; then
    echo "$json_output" | python3 -c "
import json, sys
try:
    results = json.load(sys.stdin)
    print('### 相关记忆 (top 3):')
    print()
    for i, r in enumerate(results, 1):
        shared_tag = ' [shared]' if r.get('shared') else ''
        print(str(i) + '. ' + r['file'] + shared_tag)
        print('   ' + r.get('summary', '')[:120])
        print()
except:
    sys.stdout.write(sys.stdin.read())
" 2>/dev/null
  else
    echo "(无相关记忆)"
  fi

  if [[ -n "$elapsed_ms" ]]; then
    local ms_num="${elapsed_ms%ms}"
    if [[ "$ms_num" =~ ^[0-9]+$ ]] && [[ "$ms_num" -gt 500 ]]; then
      err "Recall took ${elapsed_ms} (target: <500ms)"
    elif [[ "$ms_num" =~ ^[0-9]+$ ]]; then
      ok "Recall completed in ${elapsed_ms}"
    fi
  fi
  echo ""
}

# ─── after-task ───────────────────────────────────────────────────────────────
hook_after_task() {
  local task="$1"
  local result_file="${2:-}"
  local slug
  slug=$(echo "$task" | sed 's/[^a-zA-Z0-9\u4e00-\u9fff]/_/g' | tr -s '_' | cut -c1-60 | tr '_' '-')

  log "after-task save: ${task:0:60}"

  local today
  today=$(date +%Y-%m-%d)
  local date_dir="$MEMORY_DIR/$today"
  mkdir -p "$date_dir"

  local output_file="$date_dir/${AGENT_ID}-${slug}.md"

  # FIX: Read result file via Python argv to prevent command injection in heredoc.
  # Previously used: result_content=$(cat "$result_file") then embedded in heredoc,
  # which would execute $(...) or `...` in the file content via bash expansion.
  python3 -c "
import sys, os, re
from datetime import datetime

task         = sys.argv[1]
agent_id     = sys.argv[2]
output_file  = sys.argv[3]
result_file  = sys.argv[4] if len(sys.argv) > 4 else ''

result_content = ''
if result_file and os.path.exists(result_file):
    try:
        with open(result_file) as f:
            result_content = f.read()
    except Exception:
        result_content = ''

# Extract tags from task
text = (task + ' ' + result_content).lower()
words = re.findall(r'\b[a-z][a-z0-9]{2,}\b', text)
stop = {'the','and','for','with','from','this','that','task','agent','memory',
        'hook','after','before','python','file','path','dir','function','class',
        'method','def','return','import','export','default','none','null',
        'true','false','code','use','used','note','make','new','set','get'}
tags = sorted(set(w for w in words if w not in stop))[:8]

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('## ' + task + '\n\n')
    f.write('**Agent:** ' + agent_id + '\n')
    f.write('**时间:** ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    f.write('**Shared:** false\n\n')
    f.write('### 任务描述\n')
    f.write(task + '\n\n')
    f.write('### 关键输出\n')
    f.write(result_content + '\n\n')
    f.write('### 标签\n')
    for tag in tags:
        f.write('  - ' + tag + '\n')
    f.write('\n')
" "$task" "$AGENT_ID" "$output_file" "$result_file"

  ok "Saved → $output_file"

  # Rebuild indexes
  if [[ -x "$WAL_SNAPSHOT" ]]; then
    bash "$WAL_SNAPSHOT" rebuild &
  elif [[ -f "$WAL_SNAPSHOT" ]]; then
    bash "$WAL_SNAPSHOT" rebuild &
  else
    python3 "$INDEXER" build --agent-id "$AGENT_ID" 2>/dev/null || true
    python3 "$BM25" --build --agent-id "$AGENT_ID" 2>/dev/null || true
    ok "Indexes rebuilt"
  fi
}

# ─── dag-link ────────────────────────────────────────────────────────────────
hook_dag_link() {
  local memory_id="$1"
  local linked_id="$2"
  local reason="${3:-}"
  local dag_file="$MEMORY_DIR/dag/links.json"
  mkdir -p "$MEMORY_DIR/dag"

  # FIX: Use Python json.dumps to safely serialize all fields (prevents JSON injection).
  # Previously $reason was embedded directly via printf with no escaping.
  python3 -c "
import json, sys, os
from datetime import datetime

memory_id = sys.argv[1]
linked_id = sys.argv[2]
reason    = sys.argv[3]
agent_id  = sys.argv[4]
dag_file  = sys.argv[5]

new_link = {
    'from': memory_id,
    'to': linked_id,
    'reason': reason,
    'agent_id': agent_id,
    'created_at': datetime.now().isoformat()
}

if os.path.exists(dag_file):
    try:
        with open(dag_file) as f:
            arr = json.load(f)
    except Exception:
        arr = []
else:
    arr = []

arr.append(new_link)

with open(dag_file, 'w') as f:
    json.dump(arr, f, ensure_ascii=False, indent=2)
" "$memory_id" "$linked_id" "$reason" "$AGENT_ID" "$dag_file" 2>/dev/null && ok "DAG link: $memory_id → $linked_id" || err "Failed to write DAG link"
  ok "DAG link: $memory_id → $linked_id"
}

# ─── main ───────────────────────────────────────────────────────────────────
MODE="${MEMORY_HOOK_MODE:-${1:-}}"

case "$MODE" in
  before-task)
    [[ -z "${2:-}" ]] && { err "Usage: $0 before-task <task>"; exit 1; }
    hook_before_task "$2"
    ;;
  after-task)
    [[ -z "${2:-}" ]] && { err "Usage: $0 after-task <task> [file]"; exit 1; }
    hook_after_task "$2" "${3:-}"
    ;;
  dag-link)
    [[ -z "${3:-}" ]] && { err "Usage: $0 dag-link <id> <linked_id> [reason]"; exit 1; }
    hook_dag_link "$2" "$3" "${4:-}"
    ;;
  build)
    python3 "$INDEXER" build --agent-id "$AGENT_ID"
    python3 "$BM25" --build --agent-id "$AGENT_ID"
    ok "All indexes built"
    ;;
  search)
    shift
    python3 "$INDEXER" search "$@"
    ;;
  -h|--help|help|'')
    usage
    ;;
  *)
    err "Unknown mode: $MODE"
    usage
    exit 1
    ;;
esac
