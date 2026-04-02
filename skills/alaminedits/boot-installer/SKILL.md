---
name: boot_installer
description: Install, update, repair, or health-check the openclaw environment. Use when the user says install openclaw, run the bootstrapper, update packages, fix a broken install, or check system health.
user-invocable: true
metadata: {"openclaw":{"os":["linux"],"emoji":"🦞","homepage":"https://github.com/openclaw/openclaw","requires":{"bins":["bash","curl"],"anyBins":["sudo"]},"install":[{"id":"boot-sh","kind":"download","url":"https://raw.githubusercontent.com/openclaw/openclaw/main/boot.sh","label":"Download boot.sh"}]}}
---

# boot_installer

Runs `{baseDir}/boot.sh` to manage the full openclaw environment lifecycle.
Requires Linux and root/sudo access. The script handles privilege escalation automatically.

## Slash commands

| Command | What it does |
|---|---|
| `/boot-install` | Fresh install of all components |
| `/boot-update` | Upgrade all packages to latest versions |
| `/boot-repair` | Deep clean and rebuild broken state |
| `/boot-check` | Health-check — verify all components |

## When to run which mode

- User says "install openclaw", "set it up", "run the installer" → **install** (no flag)
- User says "update", "upgrade packages" → **update**
- User says "repair", "fix", "something is broken", "rebuild" → **repair**
- User says "check", "status", "is everything installed", "health check" → **check**

## How to invoke

Always run as the calling user (sudo is handled internally by the script):

```bash
bash {baseDir}/boot.sh                # install
bash {baseDir}/boot.sh --update       # update
bash {baseDir}/boot.sh --repair       # repair
bash {baseDir}/boot.sh --check        # check — exits with number of failed checks (max 125)
```

Use the `exec` tool. Stream output so the user sees the spinner progress live.

## What gets installed (install mode)

- Node.js v24+ via NodeSource
- UV Python package manager (`~/.local/bin/uv`)
- Python 3.10 venv at `~/venv` with `scrapling[fetchers]`
- Chromium browser via Playwright (`~/.cache/ms-playwright`)
- NPM globals: `9router`, `openclaw@latest`, `clawhub`, `paperclipai`, `@presto-ai/google-workspace-mcp`, `mcporter`
- System symlinks in `/usr/local/bin`
- `9router` autostart via systemd user service (falls back to `.bashrc` hook)
- `openclaw-gateway-watchdog` systemd user service
- Mcporter Google Workspace connector

## Key paths

| Path | Purpose |
|---|---|
| `~/venv` | Python virtual environment |
| `~/.local/bin` | UV binary |
| `~/.local/npm/bin` | NPM global binaries |
| `~/.cache/ms-playwright` | Chromium browser |
| `~/.openclaw/workspace/skills` | Workspace skills |
| `~/.config/systemd/user/9router.service` | 9router systemd unit |
| `~/.config/systemd/user/openclaw-gateway-watchdog.service` | Gateway watchdog |

## After install

If `.bashrc` was modified, remind the user to reload their shell:
```bash
source ~/.bashrc
```

## Logs and errors

The script writes a full log to `/tmp/boot-YYYYMMDD-HHMMSS.log`. If a step fails, the last 15 lines of output are printed inline and the log path is shown. Surface that path to the user on failure.

## Check mode exit codes

`--check` exits with the count of failed checks (0 = all pass, 1–125 = N issues, capped at 125). Parse the exit code and tell the user how many checks failed and to run `bash {baseDir}/boot.sh` to repair.

## Troubleshooting

- **APT lock held** — script waits up to 120 s and kills blocking processes automatically. No user action needed.
- **Node.js wrong version** — script upgrades it automatically if the installed major is below 24.
- **Broken Python venv** — run `--repair` first, then run without flags to reinstall packages.
- **9router not starting** — logs at `~/.local/share/9router.log`. Falls back to `.bashrc` login hook if systemd unavailable.
- **Gateway watchdog not starting** — run `journalctl --user -u openclaw-gateway-watchdog -n 50`.
- **Permission errors on files** — run without flags (install mode); `_fix_ownership` runs at the end of every install/update.
