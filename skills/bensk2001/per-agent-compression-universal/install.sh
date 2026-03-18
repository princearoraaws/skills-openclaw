#!/bin/bash
# Per-Agent Memory Compression Skill - Universal Installer v1.2.0
# Auto-discovers agents and registers compression tasks with full feature set

set -e

echo "🎯 Installing Per-Agent Memory Compression Skill (Universal) v1.2.0"
echo ""

# 1. Pre-checks
echo "🔍 Running pre-installation checks..."

if ! command -v openclaw &> /dev/null; then
  echo "❌ openclaw CLI not found in PATH"
  exit 1
fi

if ! openclaw agents list --json &> /dev/null; then
  echo "❌ openclaw agents list failed - is Gateway running?"
  exit 1
fi

echo "✅ Pre-checks passed"
echo ""

# 2. Discover agents with workspaces
AGENTS_JSON=$(openclaw agents list --json 2>&1)

AGENTS=$(echo "$AGENTS_JSON" | jq -r '.[] | select(.workspace != null) | "\(.id)=\(.workspace)"' 2>/dev/null)
if [ -z "$AGENTS" ]; then
  echo "❌ No agents with workspace found"
  exit 1
fi

echo "📋 Discovered agents:"
echo "$AGENTS" | while IFS='=' read -r id ws; do
  echo "  ✅ $id → $ws"
done
echo ""

# 3. Define domain context for known agents
declare -A DOMAIN_CONTEXT
DOMAIN_CONTEXT[main]="general (main agent - overall user context)"
DOMAIN_CONTEXT[hrbp]="HR/work-related (hrbp agent - professional, career, organizational development)"
DOMAIN_CONTEXT[parenting]="Parenting/family (parenting agent - children, education, family dynamics)"
DOMAIN_CONTEXT[decoration]="Renovation/decoration (decoration agent - construction, materials, project management)"
# Default for unknown agents
DOMAIN_CONTEXT[default]="agent-specific (adapt based on agent's identity and role)"

# 4. Staggered schedule offsets (minutes from 03:00 Sunday)
OFFSETS=(0 30 60 90 120 150 180 210 240 270)

INDEX=0
TASK_IDS=()
echo "$AGENTS" | while IFS='=' read -r agent_id workspace; do
  OFFSET=${OFFSETS[$INDEX]}
  INDEX=$((INDEX + 1))
  
  HOUR=$((3 + OFFSET / 60))
  MINUTE=$((OFFSET % 60))
  CRON="${MINUTE} ${HOUR} * * 0"
  
  TASK_NAME="per_agent_compression_${agent_id}"
  
  # Check if task exists
  if openclaw cron list --json 2>/dev/null | jq -e --arg name "$TASK_NAME" '.jobs[] | select(.name == $name)' >/dev/null; then
    echo "  ⚠️  Task $TASK_NAME already exists, skipping"
    continue
  fi
  
  echo "  📝 Creating: $TASK_NAME ($CRON)"
  
  # Determine domain context
  DOMAIN="${DOMAIN_CONTEXT[$agent_id]:-$DOMAIN_CONTEXT[default]}"
  
  # Build task message in a temporary file to avoid CLI length limits
  MSGFILE=$(mktemp)
  cat > "$MSGFILE" <<EOF
AUTONOMOUS: Weekly per-agent memory consolidation for '$agent_id'.

WORKSPACE: $workspace
DAILY_NOTES_DIR: {WORKSPACE}/memory
PROCESSED_DIR: {WORKSPACE}/memory/processed
STATE_FILE: {WORKSPACE}/memory/.compression_state.json
TARGET_FILES: USER.md, IDENTITY.md, SOUL.md, MEMORY.md

DOMAIN_CONTEXT: "$DOMAIN"

EXECUTION PLAN:
1. Pre-check: Verify paths exist and writable. Abort if missing.
2. Load STATE_FILE if exists, else init with {last_compressed_date: null, processed_notes: [], last_run_at: null, status: "idle"}.
3. List notes: {DAILY_NOTES_DIR}/*.md (exclude processed/). Filter: YYYY-MM-DD.md, date < today-7, not in processed_notes.
4. Sort by date (oldest first). Limit: process up to 5 notes per run.
5. FOR EACH note (max 5):
   a. Read full content.
   b. Extract: user preferences, key decisions, personal information relevant to DOMAIN_CONTEXT.
   c. Dedupe: check target files for entries with same note date; skip if found.
   d. Append to each TARGET_FILE with date header:
      - USER.md: under "## Personal Info / Preferences", add "### [YYYY-MM-DD]\n" + bullet points
      - IDENTITY.md: under "## Notes" (create if missing), header "### [YYYY-MM-DD]\n"
      - SOUL.md: under "## Principles" or "## Boundaries" as appropriate, header "### [YYYY-MM-DD]\n"
      - MEMORY.md: under "## Key Learnings" (create if missing), format "- [YYYY-MM-DD] <summary>\n"
   e. After successful appends: move note file to {PROCESSED_DIR}/ (create dir if needed); update state.processed_notes and last_compressed_date.
6. After loop: state.last_run_at = now (ISO), status="completed", write STATE_FILE; clean working buffer ({WORKSPACE}/working-buffer.md).
7. Deliver announce summary: agent processed, notes count (this run), remaining old notes count, any errors.

IMPORTANT:
- Extract ONLY factual & explicit info; DO NOT infer.
- Append only; never overwrite existing content.
- Continue on error for individual notes; log and proceed.
- If no old notes found, exit quietly (state unchanged).
- Date header format: "### [YYYY-MM-DD]" (no content on header line).

See skill README for execution details and troubleshooting.

Execute without waiting.
EOF

  # Create the task using message file to avoid length limits
  if openclaw cron add \
    --name "$TASK_NAME" \
    --cron "$CRON" \
    --tz "Asia/Shanghai" \
    --agent "main" \
    --message-file "$MSGFILE" \
    --model "openrouter/stepfun/step-3.5-flash:free" \
    --timeout 1200 \
    --session "isolated" \
    --announce \
    --channel "dingtalk-connector" \
    --to "05566651511149398" \
    --best-effort-deliver 2>&1; then
    TASK_IDS+=("$TASK_NAME")
    rm -f "$MSGFILE"
  else
    echo "    ❌ Failed to create task $TASK_NAME"
    rm -f "$MSGFILE"
  fi
done

echo ""
echo "✅ Installation complete!"
echo ""
if [ ${#TASK_IDS[@]} -gt 0 ]; then
  echo "📋 Created ${#TASK_IDS[@]} task(s):"
  for tid in "${TASK_IDS[@]}"; do
    echo "   - $tid"
  done
  echo ""
  echo "💡 Verify: openclaw cron list | grep per_agent_compression"
  echo "💡 Uninstall: ./uninstall.sh"
else
  echo "⚠️  No new tasks were created (all may already exist)"
fi
