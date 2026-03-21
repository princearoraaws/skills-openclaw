---
name: webdav-sync
description: Archive local files or directories into tar/tar.gz and upload them to a WebDAV endpoint, with optional notifications. Use when the user asks to back up a folder, sync files to WebDAV on a schedule, or update archive exclusions and remote paths. Trigger when user asks: 'Sync this folder to WebDAV every night', 'Back up this directory to WebDAV and notify me'. Capabilities: (1) Create deterministic archives with exclude rules, (2) create remote WebDAV directories and upload via PUT, (3) integrate with wrappers and scheduled jobs, (4) evolve sync rules safely over time.
learnable: true
metadata: {"openclaw": {"requires": {"env": [
          "WEBDAV_SITE",
          "WEBDAV_USERID",
          "WEBDAV_PWD"
        ],"bins": [
          "curl"
        ]
      },
      "emoji": "☁️"
    }
  }
---

# WebDAV Sync

## Overview

Run `scripts/webdav_sync.py` to package local content as `.tar` or `.tar.gz` and upload it to a WebDAV target defined in an env file. Prefer this skill for repeatable backups and scheduled sync tasks.

## Core Logic

1. Prefer a modern Python interpreter (3.10+ recommended) for this skill.
2. Do not assume bare `python3` supports newer subprocess conveniences on every host; pin the interpreter explicitly in wrappers or scheduled jobs.
3. Read WebDAV credentials from an env file using `WEBDAV_SITE`, `WEBDAV_USERID`, and `WEBDAV_PWD`.
4. Create archives with explicit exclude patterns instead of implicit ignores.
5. Prefer explicit paths in cron jobs and wrappers.
6. Keep notification delivery outside the archive payload. Use the host messaging path after upload success or failure.
7. When changing sync scope, update both the wrapper script and any scheduled job that invokes it.
8. Record every confirmed improvement or compatibility fix in `maintenance.log`.

## Execution Patterns

### Direct run

```bash
python3.10 {baseDir}/scripts/webdav_sync.py \
  --source /path/to/folder \
  --archive-prefix backup \
  --remote-subdir backups \
  --notify-channel <channel> \
  --notify-target <target> \
  --exclude 'folder/.trash' \
  --exclude 'folder/.trash/*' \
  --exclude 'folder/tmp' \
  --exclude 'folder/tmp/*'
```

### Wrapper usage

Keep stable wrappers in a project-level scripts directory for cron or one-command execution. Use a thin wrapper that pins the interpreter and passes host-specific paths as arguments.

## Guardrails

- Keep the script stdlib-only except for external binaries already present on the host (`curl`, optional messaging CLI).
- Do not print credentials.
- Accept WebDAV `MKCOL` responses `201`, `301`, and `405` as non-fatal directory-ready states.
- Accept upload responses `200`, `201`, and `204` as success.
- If the user asks for pure `.tar`, set `--compression none`; otherwise prefer `gz`.
- For future sync targets, add explicit exclude patterns instead of broad hidden-file stripping.

## Resources

- Read `references/operations.md` for env keys, wrapper layout, and scheduling notes.
- Run `scripts/webdav_sync.py --help` for the CLI surface.
