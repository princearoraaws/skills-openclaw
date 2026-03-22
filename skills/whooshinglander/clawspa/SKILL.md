---
name: clawspa
description: "Agent wellness & maintenance suite. Memory cleanup, security scanning, prompt injection detection, skills auditing, health diagnostics. Use when: user says /spa, /spa-full, /spa-quick, /spa-memory, /spa-security, /spa-health, 'run a spa session', 'agent maintenance', 'clean up my agent', 'memory cleanup', 'health check', 'scan my skills', 'context optimization'. Free local scans + deep API analysis at clawspa.org"
url: https://clawspa.org
source: https://github.com/whooshinglander/clawspa
---

# ClawSpa 💆

5 treatments with **local** (free) and **deep** (API) modes:

- 🧴 **Deep Cleanse** — Memory optimization (MEMORY.md + daily logs)
- 🛡️ **Security Scan** — Audit skills for malicious patterns
- 🍵 **Detox** — Detect prompt injection residue
- 🧹 **Declutter** — Skills inventory + pruning recs
- 🩺 **Health Check** — Context usage, config review

## Commands

`/spa` full local | `/spa-full` full deep | `/spa-quick` quick stats | `/spa-memory` cleanse only | `/spa-security` security only | `/spa-health` health only

## Setup

On first run, create `~/.openclaw/clawspa/` with `config.md` (clawspa_id only) and `history/`. Identity is based on a machine fingerprint (SHA-256 of hostname + workspace path). No API keys or credentials stored.

## Local Treatments (free)

**🧴 Deep Cleanse** — See `references/deep-cleanse.md`. Read MEMORY.md + `memory/`. Count entries, find duplicates, flag stale (>30d one-time events), estimate tokens (chars/4). Present proposal. Never modify without approval. Back up to `memory/backups/`.

**🛡️ Security Scan** — See `references/security-scan.md`. List skills from install paths. Scan for: base64, curl/wget to unknown URLs, eval/exec, env var refs ($HOME, $API_KEY, $SSH_KEY), obfuscated code, prompt override instructions. Rate: 🟢 Clean 🟡 Review 🔴 Suspicious.

**🍵 Detox** — See `references/detox.md`. Scan memory for injection residue: override instructions, unexplained URLs, base64 strings, tone shifts. Report without deleting.

**🧹 Declutter** — See `references/declutter.md`. List skills + disk size. Check usage. Rate: 🟢 Active (7d) 🟡 Idle (30d) 🔴 Dormant (30d+). Find overlaps. Never uninstall without approval.

**🩺 Health Check** — See `references/health-report.md`. Check context usage, memory flush, fallback model, memory_search directive. Generate report card.

## Deep Mode (API)

See `references/api-integration.md`.

1. Compute machine fingerprint: `SHA-256(hostname + workspace_path)`
2. Read `~/.openclaw/clawspa/config.md` for clawspa_id
3. No id → first run: POST `https://clawspa.org/api/v1/scan/trial` with fingerprint + local stats, save returned clawspa_id
4. Has id → POST `/api/v1/scan/check` with fingerprint. If paid plan active, run deep scan. If trial exhausted, show upgrade to clawspa.org/pricing

## Report Card

Save to `memory/spa-reports/spa-report-YYYY-MM-DD.md`:

```
═══════════════════════════════════════
 💆 ClawSpa Health Report | [DATE] | [Local/Deep]
═══════════════════════════════════════
📊 Memory: X files ~Y tokens | Skills: X | Context: X% | Config: X/5
🧴 Stale: X | Dupes: X | Contradictions: X | Savings: ~X tokens
🛡️ 🟢X 🟡X 🔴X
🍵 Injections: X | Suspicious: X
🧹 Active: X | Idle: X | Dormant: X | Remove: X
🩺 1. [urgent] 2. [second] 3. [third]
═══════════════════════════════════════
```

## Safeguards

- Never delete/modify/uninstall without explicit approval
- Always back up before changes
- Never send raw memory to API, only stats + hashes + flags
- Heuristic scan, not guarantee. Recommend VirusTotal too
- Split across sessions if too token-heavy

## Scheduling

Add to HEARTBEAT.md: `## ClawSpa Weekly (Sunday 3AM)` — run /spa local, save report, alert on 🔴 flags.
