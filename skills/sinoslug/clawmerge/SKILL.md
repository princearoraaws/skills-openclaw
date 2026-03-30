---
name: clawmerge
version: 3.0.8
description: OpenClaw workspace backup and restore tool with merge mode.
Unique features: Merge restore, Cron backup, Session backup
---

# Clawmerge - Workspace Backup/Restore

Simple backup and restore tool for OpenClaw workspace.

## Features

- Backup workspace with exclusions
- Restore with merge mode
- Dry-run preview
- Cron tasks backup
- Session records backup

## Usage

### Backup
./one-click-backup.sh [output_dir]

### Restore  
./one-click-restore.sh backup.tar.gz

### Options
--dry-run  : Preview only
--with-sessions : Include session records

---
