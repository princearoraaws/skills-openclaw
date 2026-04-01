# OpenClaw Memory System Plugin

> Persistent memory system for OpenClaw multi-agent workflows — **zero external dependencies**, pure Python BM25 + keyword indexing, DAG association graph, and session lifecycle hooks.

[**中文**](README_zh.md) · [**日本語**](README_ja.md)

---

## Features

- **BM25 Semantic Search** — Pure Python Okapi BM25 implementation, no pip packages required
- **Keyword Index** — Fast token-based indexing with `shared` flag and agent isolation
- **Lifecycle Hooks** — `before-task` recall + `after-task` save CLI
- **DAG Association** — Typed directed links between memory entries, BFS path finding
- **WAL Snapshot** — Non-blocking index rebuild, sub-500ms recall
- **Multi-Agent** — Agent-scoped memory isolation + cross-agent shared memories

## Installation

```bash
# Install from GitHub
git clone https://github.com/0xcjl/openclaw-memory-plugin.git
openclaw plugins install ./openclaw-memory-plugin

# Or from ClawhHub (once published)
openclaw plugins install @0xcjl/openclaw-memory-plugin
```

Restart the gateway:
```bash
openclaw gateway restart
```

## Quick Start

```bash
# Build indexes
./scripts/memory-hook.sh build

# Recall before a task (< 500ms)
./scripts/memory-hook.sh before-task "optimize Vue rendering"

# Save after a task
./scripts/memory-hook.sh after-task "completed refactor" /tmp/result.md

# Search memories
python3 scripts/bm25_search.py --search "Docker CI/CD" --top 5

# Build DAG links
python3 scripts/dag-builder.py build
```

## Project Structure

```
openclaw-memory-plugin/
├── openclaw.plugin.json   # Plugin manifest
├── scripts/
│   ├── memory-indexer.py  # Keyword index + search
│   ├── bm25_search.py      # Pure Python BM25
│   ├── memory-hook.sh      # Lifecycle CLI
│   ├── dag-builder.py       # DAG builder
│   └── wal-snapshot.sh     # WAL snapshot
├── skills/
│   └── memory-recall/
│       └── SKILL.md
└── docs/
    └── ARCHITECTURE.md
```

## Scoring

```
combined_score = bm25_norm × 0.6 + weight × 0.2 + keyword_overlap × 0.2
```

| Component | Range | Weight |
|-----------|-------|--------|
| `bm25_norm` | 0–1 | 60% |
| `weight` | 0–1 | 20% |
| `keyword_overlap` | 0–1 | 20% |

## Memory TTL

| Class | Meaning | Auto-expiry |
|-------|---------|-------------|
| P0 | Core identity, key configs | Never |
| P1 | Project decisions, progress | ~90 days |
| P2 | Debug, temporary | ~30 days |

## Requirements

- Python 3 (stdlib only — **no pip packages**)
- Bash
- OpenClaw gateway

## License

MIT
