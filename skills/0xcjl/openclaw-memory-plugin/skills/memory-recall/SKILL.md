# memory-recall

## What it does

Exposes the OpenClaw Memory System tools to any OpenClaw agent via natural language.

This skill provides the memory recall and search interface used by the皮皮虾 (main agent) memory lifecycle hooks:

- **before-task recall** — query relevant past memories before starting a new task
- **after-task save** — write completed task output to the persistent memory store
- **memory search** — BM25-ranked full-text search over all memories
- **memory build** — trigger index rebuild after bulk writes
- **DAG linking** — associate memory entries into an associative graph

## Tools

| Tool | Description |
|------|-------------|
| `memory_recall` | Recall top-N relevant memories before a task. Uses BM25 + keyword hybrid search. |
| `memory_save` | Save a completed task output to memory with auto-tagging. |
| `memory_search` | Full-text BM25 search over the memory store. |
| `memory_build` | Rebuild keyword and BM25 indexes (WAL snapshot). |
| `memory_dag_link` | Record a directed link between two memory entry IDs. |

## Usage

```
You: recall memories about Vue performance optimization
→ calls memory_recall(task="Vue performance optimization")

You: save this task: "Completed Vue component refactor"
→ calls memory_save(task="Completed Vue component refactor", result="...")

You: search memories for Docker deployment issues
→ calls memory_search(query="Docker deployment issues")

You: rebuild the memory indexes
→ calls memory_build()

You: link memory entry abc123 to def456 as "follow-up task"
→ calls memory_dag_link(fromId="abc123", toId="def456", reason="follow-up task")
```

## Direct script access

The underlying scripts can also be called directly from the shell:

```bash
# Recall before task (fast, <500ms target)
memory-hook.sh before-task "optimize Vue rendering"

# Save after task
memory-hook.sh after-task "completed Vue optimization" /tmp/result.txt

# Full index rebuild
memory-hook.sh build

# BM25 search
python3 scripts/bm25_search.py --search "Docker CI/CD" --top 5 --json

# Keyword index search
python3 scripts/memory-indexer.py search "Docker CI/CD" --agent-id dev --top 5

# DAG: auto-build from shared tags
python3 scripts/dag-builder.py build

# DAG: find shortest path between two entries
python3 scripts/dag-builder.py paths abc123 def456

# WAL snapshot
bash scripts/wal-snapshot.sh rebuild
```

## Architecture

See [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for the full system design.

## Memory index schema

Entries in `memory/index.json`:

```json
{
  "id": "sha256_hex",
  "file": "YYYY-MM-DD/agent-slug.md",
  "agent_id": "dev",
  "shared": false,
  "tags": ["vue", "performance"],
  "weight": 0.8,
  "p": "P1",
  "summary": "...",
  "keywords": ["tokenized", "terms"],
  "bm25_doc": ["pre-tokenized", "terms"]
}
```

## Scoring formula

```
combined_score = bm25_norm × 0.6 + weight × 0.2 + keyword_overlap × 0.2
```

## Requirements

- Python 3 (standard library only — no pip packages)
- Bash
- OpenClaw gateway (for tool registration)
