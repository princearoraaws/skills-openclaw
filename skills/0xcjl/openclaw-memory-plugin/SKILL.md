# OpenClaw Memory System

Persistent memory system for OpenClaw multi-agent workflows.

## Features

- BM25 semantic search with keyword fallback
- Keyword-based memory indexing  
- DAG-based memory association linking
- Session lifecycle hooks (before/after task)
- WAL snapshot for crash recovery

## Tools

- `memory_recall` - Recall top-N memories before a task
- `memory_save` - Save task output to memory
- `memory_search` - BM25 full-text search
- `memory_build` - Rebuild all indexes
- `memory_dag_link` - Link two memory entries

## Usage

Install via OpenClaw gateway plugin manager.

## Architecture

See `docs/ARCHITECTURE.md` for full details.

## License

MIT
