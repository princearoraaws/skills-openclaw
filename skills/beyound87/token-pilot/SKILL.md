---
name: token-pilot
description: Automatic token optimization during interaction. Behavioral rules + plugin synergy + workspace analyzer. Pure Node.js, cross-platform. Activate on session start (rules auto-apply) or when user asks about token usage/cost/audit.
version: 1.2.0
author: beyou
---

# Token Pilot

## Auto-Apply Rules

These 6 rules apply every session automatically. No scripts needed.

### R1: Smart Read
`read(path, limit=30)` first. Full read only for files known <2KB.
Use `offset+limit` for surgical reads. Never blind-read >50 lines.
**Exception**: When building ACP context files (coding-lead), read project standards files fully — incomplete context causes ACP failures that waste more tokens than the initial read.

### R2: Tool Result Compression
Tool result >500 chars → extract relevant portion only. Summarize, don't echo.

### R3: Response Brevity
| Query | Length |
|-------|--------|
| Yes/No, simple factual | 1-3 lines |
| How-to | 5-15 lines |
| Analysis | As needed |

"Done." is a valid reply. Never pad short answers.

### R4: No Repeat Reads
Never re-read a file unless modified since last read or explicitly asked.

### R5: Batch Tool Calls
Independent calls → one block. `read(A) + read(B) + read(C)` not three round-trips.

### R6: Output Economy
- `edit` over `write` when <30% changes
- Show changed lines + 2 context, not full files
- Filter exec output before dumping

### R7: Role-Aware Tool Economy
Infer role weight from SOUL.md at session start. No hardcoded role names — works on any team.

**Step 1 — Classify self:**
Read own SOUL.md (if present). Look for keywords:
- 🔴 Heavy role signals: `browser`, `deploy`, `code`, `engineer`, `screenshot`, `automation`, `database`, `full-stack`
- 🟡 Medium role signals: `product`, `data`, `analytics`, `growth`, `campaign`
- 🟢 Light role signals: `research`, `intel`, `content`, `write`, `report`, `summarize`, `search`

**Step 2 — Apply defaults by weight:**
| Weight | Default behavior |
|--------|-----------------|
| 🔴 Heavy | All tools available, use freely |
| 🟡 Medium | Avoid browser/canvas/tts unless task needs it |
| 🟢 Light | Avoid browser/canvas/tts/sessions_spawn/feishu_bitable unless task needs it |

**Step 3 — Override always wins:**
If user explicitly requests it, task clearly requires it, or it's the only available solution → use freely, no need to explain or ask permission.

**Fallback:** No SOUL.md found → treat as Heavy, all tools available. Never block work due to missing context.

---

## Plugin Synergy (auto-detect, graceful fallback)

### [qmd] Search Before Read
`qmd/memory_search("keyword")` → exact file+line → `read(offset, limit)`.
**Fallback**: grep / Select-String with targeted patterns.

### [smart-agent-memory] Avoid Re-Discovering
`memory recall "topic"` before investigating → skip if already solved.
After solving: `memory learn` to prevent re-investigation.
**Fallback**: `memory_search` + MEMORY.md files.

### [coding-lead] Context File Pattern
Write context to disk → lean ACP prompt ("Read .openclaw/context.md") → significant savings vs embedding.
Prefer disk context files for large context, but **include essential info (project path, stack, key constraint) directly in spawn prompt** (~200-500 chars) so ACP agent can bootstrap even if context file is missing.

ACP model awareness: claude-code (complex) → codex (quick) → direct exec (simple <60 lines).

### [multi-search-engine] Search Economy
Simple: `web_search` 3 results. Research: 5 results, `web_fetch` best one only.
**Fallback**: web_search → web_fetch (tavily 已废弃，不要配置).

### [multi-agent teams] Team Awareness
When you detect a multi-agent collaboration structure — for example shared inboxes, a dashboard, shared product knowledge, role-specific SOUL files, or recurring dispatch patterns — apply these defaults:
- Light cron or patrol tasks: `lightContext` + cheapest viable model
- Cron prompts <300 chars; move methodology into references or stable shared files
- Agent SOUL.md stays lean; detailed procedures belong in `references/` or shared workflow files
- Read minimal coordination files first, then task-specific files; avoid reloading whole team docs every turn

---

## Setup / Config / Scripts

### Setup
无需初始化。安装后规则自动生效。

### Recommended openclaw.json Config
```json
{
  "bootstrapMaxChars": 12000,
  "bootstrapTotalMaxChars": 20000,
  "compaction": {
    "mode": "safeguard",
    "memoryFlush": { "enabled": true }
  },
  "contextPruning": {
    "toolResults": { "ttl": "5m", "softTrimRatio": 0.3 }
  },
  "heartbeat": { "every": "55m", "activeHours": { "start": "08:00", "end": "23:00" } }
}
```

### Recommended tools.allow by role
- fullstack-dev / devops：read/write/edit/exec/web_search/web_fetch/browser/sessions_spawn/memory_*/message
- product-lead：read/write/edit/exec/web_search/feishu_doc/feishu_bitable/feishu_wiki/memory_*/message
- data/intel/content/growth：按轻量职责裁剪，尽量不要 `[*]`

### Scripts

```bash
# Audit (read-only diagnostics)
node {baseDir}/scripts/audit.js --all             # Full audit
node {baseDir}/scripts/audit.js --config          # Config score (5-point)
node {baseDir}/scripts/audit.js --synergy         # Plugin synergy check

# Optimize (actionable recommendations)
node {baseDir}/scripts/optimize.js                # Full scan: workspace + cron + agents
node {baseDir}/scripts/optimize.js --apply        # Auto-fix workspace (cleanup junk, delete BOOTSTRAP.md)
node {baseDir}/scripts/optimize.js --cron         # Cron model routing + lightContext + prompt compression
node {baseDir}/scripts/optimize.js --agents       # Agent model tiering recommendations
node {baseDir}/scripts/optimize.js --template     # Show optimized AGENTS.md template (~300 tok)

# Catalog
node {baseDir}/scripts/catalog.js [--output path] # Generate SKILLS.md index
```

## Config Recommendations

```json
{
  "bootstrapMaxChars": 12000,
  "bootstrapTotalMaxChars": 20000,
  "compaction": {
    "mode": "safeguard",
    "memoryFlush": { "enabled": true }
  },
  "contextPruning": {
    "toolResults": { "ttl": "5m", "softTrimRatio": 0.3 }
  },
  "heartbeat": { "every": "55m", "activeHours": { "start": "08:00", "end": "23:00" } }
}
```

### memoryFlush（新增）
Compaction 压缩长会话之前，自动把关键信息持久化到本地记忆（smart-agent-memory）。
防止重要决策/信息被 compaction 丢掉。配合 memos-local 插件效果最佳。

### contextPruning TTL（新增）
工具调用结果在 context 里保留 5 分钟后自动软裁剪（保留摘要，丢弃原始输出）。
长会话中工具结果积累是 context 膨胀的主要原因之一。

### 工具白名单（新增）
在 openclaw.json 的各 agent `tools.allow` 里设置精确白名单，而非 `["*"]`。
按角色建议：

| Agent | 核心工具 | 可以不要 |
|-------|---------|---------|
| intel-analyst | web_search/web_fetch/read/write/edit/exec/memory_*/message | browser/canvas/tts/feishu_bitable/sessions_spawn |
| data-analyst | read/write/edit/exec/web_search/feishu_bitable/memory_*/message | browser/canvas/tts/feishu_wiki |
| content-chief | read/write/edit/exec/web_search/web_fetch/feishu_doc/feishu_wiki/memory_*/message | browser/canvas/tts/feishu_bitable |
| growth-lead | read/write/edit/exec/web_search/web_fetch/feishu_doc/feishu_bitable/memory_*/message | browser/canvas/tts/feishu_wiki |
| product-lead | read/write/edit/exec/web_search/feishu_doc/feishu_bitable/feishu_wiki/memory_*/message | browser/canvas/tts |
| devops | read/write/edit/exec/web_search/web_fetch/browser/sessions_spawn/memory_*/message | canvas/tts/feishu_bitable |
| fullstack-dev | read/write/edit/exec/web_search/web_fetch/browser/sessions_spawn/memory_*/message | canvas/tts/feishu_bitable |
预计节省：每个受限 agent 减少 ~4,000-8,000 tok 工具定义开销。

## Model Routing

| Complexity | Model Tier | Examples |
|------------|-----------|---------|
| Light | Cheapest (gemini/haiku) | inbox scan, status check |
| Medium | Mid (gpt/sonnet) | web search, content |
| Heavy | Top (opus) | architecture, briefs |

## References
- `references/workspace-patterns.md` — File organization for minimal token cost
- `references/cron-optimization.md` — Cron model routing guide
