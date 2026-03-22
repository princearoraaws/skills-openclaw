#!/bin/bash

# Workspace Backup Script
# 备份两个 workspace 到 GitHub 仓库的不同分支

WORKSPACE_MAIN="$HOME/.openclaw/workspace"
WORKSPACE_FORMULAS="$HOME/.openclaw/workspace-formulas"
LOG_FILE="$HOME/.openclaw/logs/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

backup_workspace() {
    local workspace_path="$1"
    local branch="$2"
    local workspace_name="$3"

    log "Starting backup for $workspace_name (branch: $branch)"

    cd "$workspace_path" || {
        log "ERROR: Cannot cd to $workspace_path"
        return 1
    }

    # Check if there are changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        log "No changes to commit for $workspace_name"
        return 0
    fi

    # Add all changes
    git add -A

    # Commit with timestamp
    commit_msg="Backup $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$commit_msg" || {
        log "ERROR: Failed to commit for $workspace_name"
        return 1
    }

    # Push to remote
    git push origin "$branch" || {
        log "ERROR: Failed to push $workspace_name"
        return 1
    }

    log "Successfully backed up $workspace_name"
    return 0
}

# Main
log "========== Workspace Backup Started =========="

# Backup main workspace
backup_workspace "$WORKSPACE_MAIN" "main" "workspace"

# Backup formulas workspace
backup_workspace "$WORKSPACE_FORMULAS" "formulas" "workspace-formulas"

log "========== Workspace Backup Completed =========="
