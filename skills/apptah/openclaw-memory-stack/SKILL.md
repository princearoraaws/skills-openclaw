---
name: openclaw-memory-stack
description: "Total recall, 90% fewer tokens. 5-engine memory with 3-tier token control, RRF rank fusion, knowledge graph, and self-cleaning dedup. Runs offline. $49 one-time."
version: 0.2.0
metadata:
  openclaw:
    requires:
      env:
        - OPENCLAW_LICENSE_KEY
      bins:
        - bash
    primaryEnv: OPENCLAW_LICENSE_KEY
    emoji: "\U0001F9E0"
    homepage: https://openclaw-memory.apptah.com
---

# OpenClaw Memory Stack 🧠

**Total recall. 90% fewer tokens.**

Your agent forgets past decisions and burns tokens re-reading the same context. Memory Stack fixes both problems — 5 engines search in parallel, 3-tier output controls exactly how many tokens you spend, and a rescue store saves key facts before compaction eats them.

One command to install. Works in the background. No config files to edit.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    OPENCLAW MEMORY STACK                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  FTS5    │  │   QMD    │  │ Markdown │  │ Lossless │        │
│  │ keyword  │  │ semantic │  │  memory  │  │   DAG    │        │
│  │ search   │  │ + BM25   │  │  files   │  │ summary  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │              │              │              │              │
│       └──────────────┴──────┬───────┴──────────────┘              │
│                             ▼                                    │
│                    ┌────────────────┐                             │
│                    │  RRF Fusion +  │  ← Reciprocal Rank Fusion  │
│                    │  MMR Diversity │    merges all results       │
│                    └───────┬────────┘                             │
│                            ▼                                     │
│                    ┌────────────────┐                             │
│                    │  3-Tier Output │                             │
│                    │                │                             │
│                    │  L0: ~100 tok  │  ← auto-recall (default)   │
│                    │  L1: ~800 tok  │  ← summary on demand       │
│                    │  L2: full text │  ← only when needed        │
│                    └───────┬────────┘                             │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────┐        │
│  │                  RESCUE STORE                         │        │
│  │  SQLite — facts, decisions, deadlines extracted       │        │
│  │  before compaction. Survives any context window.      │        │
│  └──────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐        │
│  │               KNOWLEDGE GRAPH                         │        │
│  │  SQLite — people, tools, decisions linked.            │        │
│  │  Multi-hop BFS · PageRank · Evolution chains          │        │
│  └──────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐        │
│  │               SELF-CLEANING                           │        │
│  │  4-level dedup: exact → normalized → substring →      │        │
│  │  cosine. Health score 0-100. Runs automatically.      │        │
│  └──────────────────────────────────────────────────────┘        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Why It's Different

Most memory skills do **one thing** — vector search, or a markdown file, or a WAL log. You end up installing 3-4 skills, configuring each one, and hoping they work together.

Memory Stack is **one install** that does all of it:

| What you need | Other skills | Memory Stack |
|---|---|---|
| Find a function name | ❌ Vector search misses exact names | ✅ FTS5 keyword search finds it instantly |
| Find "how does auth work" | ✅ Vector search works | ✅ QMD semantic search + HyDE expansion |
| Find across 5 conversations | ❌ Limited to current context | ✅ Rescue store + knowledge graph |
| Control token spend | ❌ Full text every time | ✅ 3 tiers: ~100 / ~800 / full |
| Remove duplicates | ❌ Manual cleanup | ✅ 4-level auto-dedup |
| Track how decisions evolved | ❌ No history | ✅ Evolution chains in knowledge graph |
| Check memory quality | ❌ No tooling | ✅ Health score 0-100 |
| Work offline | ❌ Needs OpenAI key | ✅ Core search runs offline |

## How Token Savings Work

Every memory search costs tokens. The more text injected, the higher your API bill.

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   Native memory:     ████████████████████  ~1000 tok│
│                      (full text, every time)        │
│                                                     │
│   Memory Stack L0:   ██                     ~100 tok│
│                      (auto-recall, key facts only)  │
│                                                     │
│   Memory Stack L1:   ████████              ~800 tok │
│                      (summary, on demand)           │
│                                                     │
│   Memory Stack L2:   ████████████████████  ~1000 tok│
│                      (full text, only when needed)  │
│                                                     │
│   Savings:           90% on most searches           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**L0 is the default.** Your agent gets the answer in ~100 tokens. If it needs more detail, it requests L1 or L2. You only pay for what's needed.

## The 5 Search Engines

### Engine 1: FTS5 (Keyword)

SQLite full-text search. Best for exact names, symbols, error messages.

```bash
openclaw-memory "handleAuthCallback" --hint exact
# → Finds exact function name in 12ms
```

### Engine 2: QMD (Semantic + BM25)

Vector embeddings + BM25 hybrid. Best for concepts and behavior.

```bash
openclaw-memory "how does the payment flow handle retries" --hint semantic
# → Understands meaning, not just keywords
```

**HyDE expansion:** For semantic queries, Memory Stack generates a hypothetical answer first, then searches for documents similar to that answer. This dramatically improves recall for abstract questions — no API call needed, runs locally.

### Engine 3: Markdown Memory

Searches your MEMORY.md and memory/*.md files. Compatible with native OpenClaw memory format.

### Engine 4: Rescue Store

SQLite-backed fact extraction. When conversations get long and compaction kicks in, key facts — decisions, deadlines, requirements — are already saved here. Your agent recalls them instantly instead of you re-explaining.

### Engine 5: Lossless DAG

Hierarchical summarization tree. Large codebases get condensed into a DAG of summaries. You can drill down from high-level overview to specific details without loading everything.

### How They Work Together

```
Your query: "What did we decide about the API design?"

  FTS5:      "API design" → 2 results (score 0.4, 0.3)
  QMD:       semantic match → 3 results (score 0.8, 0.6, 0.5)
  Markdown:  file search → 1 result (score 0.5)
  Rescue:    fact lookup → 2 results (score 0.9, 0.7)
  Lossless:  DAG drill-down → 1 result (score 0.6)
                    │
                    ▼
           ┌────────────────┐
           │  RRF Fusion    │  Reciprocal Rank Fusion
           │  + MMR Dedup   │  merges + diversifies
           └───────┬────────┘
                   ▼
           Top 3 results, deduplicated, L0 tier (~100 tokens)
```

The router picks the right engine automatically. If one engine returns low-relevance results, it falls back to the next. You always get the best answer from the best source.

## Knowledge Graph

Not a markdown file pretending to be a graph. A real SQLite-backed knowledge graph.

```
                    ┌─────────┐
                    │  Auth   │
                    │ Module  │
                    └────┬────┘
                         │ depends_on
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌─────────┐ ┌────────┐ ┌────────┐
        │ JWT     │ │ Redis  │ │ User   │
        │ Library │ │ Cache  │ │ Model  │
        └─────────┘ └────────┘ └────┬───┘
                                    │ decided_by
                                    ▼
                              ┌──────────┐
                              │ Sprint 3 │
                              │ Decision │
                              └──────────┘
```

**What you can ask:**
- "What depends on the auth module?" → One-hop BFS, instant answer
- "How did the database decision evolve?" → Evolution chain traversal
- "Who is the expert on payments?" → PageRank over contribution graph
- "What changed between last week and now?" → Bi-temporal query

## Self-Cleaning Memory

Duplicates cost real money every time your agent reads them.

```
Before cleanup:
  "Use React for frontend"          ← original
  "We decided to use React"         ← normalized duplicate
  "Use React for the frontend UI"   ← substring duplicate
  "Frontend framework: React"       ← cosine duplicate

After 4-level dedup:
  "Use React for frontend"          ← one clean entry

Health score: 47 → 92
```

**4 dedup levels:**
1. **Exact** — identical strings
2. **Normalized** — same after lowering case, trimming whitespace
3. **Substring** — one entry contains another
4. **Cosine** — semantically identical but differently worded

Runs automatically. Health score 0-100 tells you exactly how clean your memory is.

## Setup

```bash
# 1. Run setup with your license key
./setup.sh --key=oc-starter-YOUR_KEY

# 2. Restart OpenClaw — memory is active immediately
openclaw gateway restart

# 3. Initialize in your project
openclaw-memory init .
openclaw-memory embed

# 4. Just talk — memory works in the background
openclaw-memory "your query here"
```

Run `./setup.sh --help` for all options.

### Verify Installation

```bash
# Check all engines
openclaw-memory health

# Expected output:
# [OK] fts5     — ready
# [OK] qmd      — ready (or: installed, run 'openclaw-memory embed')
# [OK] markdown  — ready
# [OK] rescue   — ready
# [OK] lossless — ready
# Health: 5/5 engines operational

# Deep check (tests actual search)
openclaw-memory health --deep
```

### Optional: Add LLM for Fact Extraction

Core search works offline. Add any LLM key to unlock automatic fact extraction from every conversation:

```bash
# Any of these — Memory Stack auto-detects
export OPENAI_API_KEY="sk-..."        # OpenAI
export ANTHROPIC_API_KEY="sk-ant-..." # Anthropic
export OLLAMA_HOST="localhost:11434"   # Ollama (free, local)
# Or any OpenAI-compatible endpoint
```

A few cents per session saves dollars of wasted tokens.

## Requirements

| Dependency | Required | Notes |
|---|---|---|
| bash | Yes | macOS / Linux / Windows via WSL2 |
| OpenClaw | Yes | 2026.3.2 or later |
| Bun | Recommended | For QMD vector search (free, open source) |
| Python 3 | Optional | Used by some backends for JSON processing |
| LLM API key | Optional | Any provider. Unlocks fact extraction |

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| No search results | Project not indexed | Run `openclaw-memory init . && openclaw-memory embed` |
| QMD unavailable | Bun not installed | Install Bun: `curl -fsSL https://bun.sh/install \| bash` |
| Low relevance scores | Wrong search mode | Use `--hint exact` for names, `--hint semantic` for concepts |
| Stale results | Index outdated | Run `openclaw-memory embed` to re-index |
| Health score low | Duplicates accumulated | Dedup runs automatically; check with `openclaw-memory health` |
| Rescue store empty | No LLM key configured | Add any API key (see Optional setup above) |
| Slow first search | Embedding cold start | Normal on first run. Subsequent searches are fast |

## vs Native Memory

| | Native | Memory Stack |
|---|---|---|
| Search engines per query | 2 (keyword + vector) | 5, merged by RRF with per-engine weights |
| Token control | Full text every time | 3 tiers: L0 ~100 / L1 ~800 / L2 full |
| Cross-conversation search | Limited | Instant via graph + rescue stores |
| Understands meaning | Basic keyword matching | HyDE expansion + semantic search |
| Duplicate handling | Can pay twice for same info | 4-level auto-dedup before sending |
| Memory health check | No | Quality score 0-100 |
| Decision tracking | No | Evolution chains in knowledge graph |
| Cost over time | Grows with junk | Self-cleaning, stays flat |
| Offline capable | Needs embedding provider | Core search runs offline |
| LLM lock-in | OpenAI only | Any provider: OpenAI, Anthropic, Ollama, MLX |

## Pricing

**$49 — one-time purchase. No subscription.**

- Up to 3 device activations
- No data leaves your machine
- Core search runs offline, no API costs
- Bug fixes within your version are free

Pays for itself in the first week of saved API costs.

**Purchase at: [openclaw-memory.apptah.com](https://openclaw-memory.apptah.com)**

---

*Built by [@Apptah](https://github.com/Apptah) — because your agent's memory shouldn't cost more than yours.*
