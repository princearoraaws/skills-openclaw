---
name: setup-doctor
description: "Diagnose and fix OpenClaw setup issues in one command. Checks Node, npm, gateway, config, and workspace. Runs in two modes: Quick (default, 10 seconds) and Full (all phases, opt-in). Multi-language support. Config and workspace checks report file existence and size only — never read contents. No credentials accessed without approval. Homepage: https://clawhub.ai/skills/setup-doctor"
---

# Setup Doctor

**Install:** `clawhub install setup-doctor`

Diagnose OpenClaw setup issues. Like `brew doctor` — one command to check everything.

## Language

Detect from the user's message language. Default: English.

Supported: English, Norwegian, German, Spanish, French, Japanese, Chinese.

## Two Modes

### 🟢 Quick Check (default)

Runs in ~10 seconds. Covers the essentials.

Trigger: "doctor check", "kjør doctor", "diagnose", "hvorfor fungerer ikke"

```bash
node --version
npm --version
openclaw gateway status 2>&1
```

Expected: Node 20+, npm 9+, gateway running.

**Report format:**

```markdown
## 🩺 Setup Doctor — Quick Check

| Check | Status | Details |
|-------|--------|---------|
| Node.js | ✅ Pass | v24.11.1 |
| npm | ✅ Pass | 10.9.2 |
| Gateway | ✅ Pass | Running (PID 1234, up 4h) |

Fixes available: none. Your setup looks healthy.
```

If issues found, show one-line fix for each:

```markdown
| Check | Status | Details | Fix |
|-------|--------|---------|-----|
| Node.js | ❌ Fail | v18.17.0 | Install Node 20+: https://nodejs.org |
| Gateway | ❌ Fail | Not running | Run: openclaw gateway start |
```

### 🔵 Full Check (opt-in)

Covers everything. Trigger: "doctor check full", "full diagnose"

Includes Quick Check phases PLUS:

**Phase 3: Configuration**
- Config file exists
- Channel config has security settings

**Phase 4: Workspace**
- Workspace directory exists, no permission issues
- Report file names and sizes only — do not read file contents

**Phase 5: Channel Verification**
- Check configured channels (Telegram, Discord, etc.) for obvious issues

**Phase 6: Common Pitfalls**
- Windows: long paths, PowerShell execution policy
- macOS: FileVault, Homebrew PATH
- Linux: systemd service enabled

**Phase 7: API Connectivity (explicit opt-in)**
Trigger: "doctor check api", "sjekk api"

1. Network reachability test (no credentials)
2. If user explicitly asks to test a specific provider key:
   - Ask which provider
   - Confirm before testing
   - Never include keys in output
   - Never test more than one per request

## Quick Commands

| User says | Action |
|-----------|--------|
| "doctor check" / "kjør doctor" | Quick Check (default) |
| "doctor check full" / "full diagnose" | Full Check (all phases) |
| "doctor check api" | API connectivity test |
| "fix it" / "fix det" | Auto-fix with confirmation |
| "setup wizard" / "oppsett" | New user setup wizard |

---

## Auto-Fix

Trigger: "fix it", "fix det"

1. Show exactly what will change
2. Get user confirmation
3. Apply fix
4. Re-run check to verify

**Never auto-fix without showing what changes.**

---

## Setup Wizard

Trigger: "setup wizard", "oppsett"

Guide new users through workspace configuration. Three profiles:

| Profile | What you get |
|---------|-------------|
| 🟢 Minimal | SOUL.md, user config, AGENTS.md |
| 🟡 Standard | + IDENTITY.md, long-term notes dir, HEARTBEAT.md |
| 🔴 Power User | + Proactive automation rules, advanced heartbeat |

Ask: name, language, timezone, agent name. Provide templates as output.

---

## Workspace Audit

Trigger: "workspace audit"

Check workspace files. Report existence and size only — never read contents.

| File | Purpose | Status |
|------|---------|--------|
| SOUL.md | Agent personality | ✅/❌ |
| User config | Name, timezone, prefs | ✅/❌ |
| AGENTS.md | Behavior rules | ✅/❌ |
| Long-term notes | Persistent memory | ✅/⚠️/❌ |
| BOOTSTRAP.md | First-run script | ⚠️ Should delete |
