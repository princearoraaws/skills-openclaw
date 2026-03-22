#!/bin/bash

# Check backup status for both workspaces

echo "=== Workspace Backup Status ==="
echo ""

echo "--- workspace (main branch) ---"
cd ~/.openclaw/workspace && git status --short 2>/dev/null || echo "Not a git repo"
echo ""

echo "--- workspace-formulas (formulas branch) ---"
cd ~/.openclaw/workspace-formulas && git status --short 2>/dev/null || echo "Not a git repo"
echo ""

echo "=== Last Backup Log ==="
tail -20 ~/.openclaw/logs/backup.log 2>/dev/null || echo "No backup log found"
