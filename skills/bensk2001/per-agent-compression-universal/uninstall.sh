#!/bin/bash
# Uninstall Per-Agent Memory Compression Skill (Universal)
# Removes all per_agent_compression_* cron tasks (note underscore)

set -e

echo "🗑️  Uninstalling Per-Agent Memory Compression Skill..."

TASKS=$(openclaw cron list --json 2>/dev/null | jq -r '.jobs[] | select(.name | test("^per_agent_compression_")) | .id')

if [ -z "$TASKS" ]; then
  echo "ℹ️  No per-agent compression tasks found. Already uninstalled?"
  exit 0
fi

COUNT=0
for TASK_ID in $TASKS; do
  if openclaw cron delete "$TASK_ID" 2>/dev/null; then
    COUNT=$((COUNT + 1))
  else
    echo "  ⚠️  Failed to delete task $TASK_ID"
  fi
done

echo "✅ Uninstalled $COUNT task(s)."
echo ""
echo "💡 Verify: openclaw cron list | grep per_agent_compression (should be empty)"
