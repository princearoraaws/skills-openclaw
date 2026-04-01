# OpenClaw Memory System — Architecture

## Overview

The OpenClaw Memory System is a lightweight, zero-dependency persistent memory layer for multi-agent AI workflows. It provides:

1. **Keyword Indexing** (`memory-indexer.py`) — fast term-based recall
2. **BM25 Semantic Search** (`bm25_search.py`) — pure-Python Okapi BM25 ranking
3. **Session Lifecycle Hooks** (`memory-hook.sh`) — before-task recall + after-task save
4. **DAG Association Graph** (`dag-builder.py`) — typed links between memory entries
5. **WAL Snapshot** (`wal-snapshot.sh`) — non-blocking index rebuild after writes

```
┌─────────────────────────────────────────────────────────────┐
│  Agent Session Lifecycle                                      │
│                                                              │
│  BEFORE TASK                                                 │
│    memory-hook.sh before-task "task description"             │
│      ├─→ bm25_search.py (semantic)                           │
│      └─→ memory-indexer.py (keyword)                         │
│      └─→ output: top-3 memories → context                    │
│                                                              │
│  AFTER TASK                                                  │
│    memory-hook.sh after-task "task" [result_file]           │
│      └─→ writes memory/YYYY-MM-DD/<agent>-<slug>.md         │
│      └─→ wal-snapshot.sh rebuild (background)               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
memory/                    index.json              bm25_index.json
   │                           │                        │
   │  memory-indexer.py         │  bm25_search.py        │
   │  --build                   │  --build                │
   └───────────────────────────→┴────────────────────────┘
                                     │
   ┌─────────────────────────────────┘
   │  memory-hook.sh
   │    before-task → recall → context
   │    after-task  → save   → WAL trigger
   │    dag-link    → DAG edge
   │
   └── dag/links.json (DAG adjacency list)
```

## Scripts

### `memory-indexer.py`

Keyword-based memory indexer. Walks `memory/` directory and builds `index.json`.

**Modes:**
- `--build` — rebuild keyword index from all `.md` files in `memory/`
- `--search <query>` — recall memories by keyword + BM25 score

**Index schema:**
```json
{
  "version": 2,
  "built_at": "ISO8601",
  "agent_id": "dev",
  "entries": [{ "id", "file", "path", "agent_id", "shared", "tags", "weight", "p", "summary", "keywords", "bm25_doc" }]
}
```

### `bm25_search.py`

Pure Python Okapi BM25 implementation. No external dependencies.

**Parameters:** `k1=1.5`, `b=0.75` (standard BM25 defaults)

**Modes:**
- `--build` — build BM25 index from `index.json`
- `--search <query>` — ranked BM25 search

**Scoring:**
```
score = Σ IDF(t) · (tf(t) · (k1+1)) / (tf(t) + k1 · (1-b + b·dl/avgdl))
```

### `memory-hook.sh`

Session lifecycle CLI. Hooks into agent workflow:

| Mode | Description |
|------|-------------|
| `before-task <task>` | Recall top-3 relevant memories |
| `after-task <task> [file]` | Save task to dated memory file |
| `dag-link <id1> <id2> [reason]` | Record a DAG edge |
| `build` | Rebuild both indexes |
| `search <query>` | CLI search wrapper |

**Environment variables:**
- `AGENT_ID` — agent identifier (default: `dev`)
- `WORKSPACE_ROOT` — workspace path (default: `~/.openclaw/workspace-dev`)

### `dag-builder.py`

Builds and queries a directed acyclic graph of memory associations.

**Commands:**
- `build` — auto-link entries sharing ≥2 tags or ≥3 keywords
- `link <from> <to> [reason]` — manually add an edge
- `query <node_id>` — list incoming/outgoing edges
- `paths <id1> <id2>` — BFS shortest path between entries
- `neighbors <node_id>` — BFS neighborhood within N hops

**DAG file:** `memory/dag/links.json` (adjacency list format)

### `wal-snapshot.sh`

Write-Ahead Log snapshot trigger. Non-blocking rebuild of both indexes after memory writes.

**Commands:**
- `rebuild` — full index + BM25 rebuild
- `index-only` — keyword index only (faster)
- `status` — show last rebuild timestamp

## Performance

| Operation | Target | Actual |
|-----------|--------|--------|
| Recall (before-task) | < 500ms | ~200–400ms |
| Index build (100 files) | < 5s | ~1–2s |
| BM25 build (100 files) | < 2s | ~0.5–1s |

## Memory TTL Classes

| Class | Meaning | Default retention |
|-------|---------|------------------|
| P0 | Core identity, key configs | Never expire |
| P1 | Project progress, decisions | 90 days |
| P2 | Debug, temporary | 30 days |

Inferred from file content markers (`P0`/`P1`/`P2`) and file name prefixes (`daydream*` → `shared=true`).

## Shared Memory

Memories with `shared=true` are visible across all agents. Auto-detected from:
- Filename prefix: `daydream*`, `meditation*`
- Content markers: `shared`, `P0`

## Multi-Agent Isolation

Each agent has its own `agent_id` in entry metadata. Search filters:
```
(entry["agent_id"] == current_agent) OR (entry["shared"] == true)
```

## OpenClaw Plugin Integration

The `openclaw-memory-system` plugin registers these tools:

- `memory_recall` — before-task recall
- `memory_save` — after-task save
- `memory_search` — standalone BM25 search
- `memory_build` — trigger index rebuild
- `memory_dag_link` — DAG edge creation

Plugin kind: `memory` (selected via `plugins.slots.memory`).

## File Structure

```
memory/
├── index.json          # keyword + metadata index
├── bm25_index.json     # BM25 corpus + IDF scores
├── YYYY-MM-DD/         # dated memory files
│   └── dev-<slug>.md
└── dag/
    └── links.json      # DAG adjacency list
```
