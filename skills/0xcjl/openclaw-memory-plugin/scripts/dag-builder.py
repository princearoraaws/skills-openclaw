#!/usr/bin/env python3
"""
dag-builder.py — Memory Association DAG builder for OpenClaw.

Builds a directed acyclic graph of memory entry associations.
Each node is a memory entry (by ID); each edge is a typed link
(from → to, with a reason).

Zero external dependencies (Python stdlib only).

Usage:
  python dag-builder.py --build              # Build DAG from memory/index.json
  python dag-builder.py --link <from> <to> <reason>
  python dag-builder.py --query <memory_id>  # Get outgoing links for an entry
  python dag-builder.py --paths <id1> <id2>  # Find shortest path between two entries
  python dag-builder.py --json               # Output raw JSON
"""

import argparse
import json
import math
import re
import sys
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─── Config ──────────────────────────────────────────────────────────────────

WORKSPACE  = Path.home() / ".openclaw" / "workspace-dev"
MEMORY_DIR = WORKSPACE / "memory"
DAG_FILE   = MEMORY_DIR / "dag" / "links.json"

# ─── Data structures ──────────────────────────────────────────────────────────

class MemoryDAG:
    """In-memory directed graph of memory associations."""

    def __init__(self):
        # adjacency: from_id → [(to_id, reason, created_at, agent_id)]
        self.edges_from: dict[str, list[dict]] = defaultdict(list)
        # reverse adjacency: to_id → [(from_id, reason, ...)]
        self.edges_to: dict[str, list[dict]] = defaultdict(list)
        self.nodes: set[str] = set()

    @classmethod
    def load(cls, dag_file: Path = DAG_FILE) -> "MemoryDAG":
        dag = cls()
        if not dag_file.exists():
            return dag
        try:
            with open(dag_file, encoding="utf-8") as f:
                links = json.load(f)
        except (json.JSONDecodeError, IOError):
            return dag

        for link in links:
            dag.add_edge(
                link["from"],
                link["to"],
                reason=link.get("reason", ""),
                agent_id=link.get("agent_id", "unknown"),
                created_at=link.get("created_at", ""),
            )
        return dag

    def save(self, dag_file: Path = DAG_FILE):
        dag_file.parent.mkdir(parents=True, exist_ok=True)
        links = []
        for from_id, to_list in self.edges_from.items():
            for to_id, reason, created_at, agent_id in to_list:
                links.append({
                    "from": from_id,
                    "to": to_id,
                    "reason": reason,
                    "created_at": created_at,
                    "agent_id": agent_id,
                })
        dag_file.write_text(
            json.dumps(links, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def add_edge(self, from_id: str, to_id: str, reason: str = "",
                 agent_id: str = "dev", created_at: str = ""):
        self.nodes.add(from_id)
        self.nodes.add(to_id)
        if created_at is None:
            created_at = datetime.now().isoformat()
        self.edges_from[from_id].append((to_id, reason, created_at, agent_id))
        self.edges_to[to_id].append((from_id, reason, created_at, agent_id))

    def get_outgoing(self, node_id: str) -> list[dict]:
        return [
            {"to": t, "reason": r, "created_at": c, "agent_id": a}
            for t, r, c, a in self.edges_from.get(node_id, [])
        ]

    def get_incoming(self, node_id: str) -> list[dict]:
        return [
            {"from": f, "reason": r, "created_at": c, "agent_id": a}
            for f, r, c, a in self.edges_to.get(node_id, [])
        ]

    def get_neighbors(self, node_id: str, depth: int = 1) -> set[str]:
        """BFS traversal to get all nodes within `depth` hops."""
        visited = set()
        queue = deque([(node_id, 0)])
        visited.add(node_id)
        while queue:
            current, d = queue.popleft()
            if d >= depth:
                continue
            for (to_id, _, _, _) in self.edges_from.get(current, []):
                if to_id not in visited:
                    visited.add(to_id)
                    queue.append((to_id, d + 1))
        visited.discard(node_id)
        return visited

    def shortest_path(self, from_id: str, to_id: str) -> Optional[list]:
        """BFS shortest path from from_id to to_id. Returns None if unreachable."""
        if from_id == to_id:
            return [from_id]
        visited = {from_id}
        queue = deque([(from_id, [from_id])])
        while queue:
            current, path = queue.popleft()
            for (next_id, _, _, _) in self.edges_from.get(current, []):
                if next_id == to_id:
                    return path + [next_id]
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))
        return None

    def build_from_index(self, index_file: Path) -> int:
        """Auto-link entries with shared tags/keywords as implicit edges."""
        if not index_file.exists():
            print(f"[dag-builder] index.json not found: {index_file}", file=sys.stderr)
            return 0

        with open(index_file, encoding="utf-8") as f:
            index = json.load(f)

        entries = index.get("entries", [])
        links_created = 0

        # Link entries that share >= 2 keywords
        for i, e1 in enumerate(entries):
            for e2 in entries[i + 1:]:
                shared_tags = set(e1.get("tags", [])) & set(e2.get("tags", []))
                shared_keywords = set(e1.get("keywords", [])) & set(e2.get("keywords", []))
                if len(shared_tags) >= 2:
                    reason = f"shared tags: {', '.join(list(shared_tags)[:5])}"
                    if not self._edge_exists(e1["id"], e2["id"]):
                        self.add_edge(e1["id"], e2["id"], reason=reason)
                        links_created += 1
                elif len(shared_keywords) >= 3:
                    reason = f"semantic overlap: {', '.join(list(shared_keywords)[:5])}"
                    if not self._edge_exists(e1["id"], e2["id"]):
                        self.add_edge(e1["id"], e2["id"], reason=reason)
                        links_created += 1

        return links_created

    def _edge_exists(self, from_id: str, to_id: str) -> bool:
        return any(t == to_id for t, _, _, _ in self.edges_from.get(from_id, []))

    def stats(self) -> dict:
        return {
            "nodes": len(self.nodes),
            "edges": sum(len(v) for v in self.edges_from.values()),
            "avg_out_degree": (
                sum(len(v) for v in self.edges_from.values()) / max(len(self.nodes), 1)
            ),
        }


# ─── CLI ─────────────────────────────────────────────────────────────────────

def cmd_build(agent_id: str = "dev") -> MemoryDAG:
    index_file = MEMORY_DIR / "index.json"
    dag_file   = DAG_FILE

    existing = MemoryDAG.load(dag_file)
    new_links = existing.build_from_index(index_file)

    if new_links > 0:
        existing.save(dag_file)
        print(f"[dag-builder] Added {new_links} auto-links → {dag_file}")
    else:
        print("[dag-builder] No new auto-links (entries may already be connected)")

    stats = existing.stats()
    print(f"[dag-builder] DAG stats: {stats['nodes']} nodes, {stats['edges']} edges, "
          f"avg out-degree={stats['avg_out_degree']:.2f}")
    return existing


def cmd_link(from_id: str, to_id: str, reason: str = "", agent_id: str = "dev") -> None:
    dag = MemoryDAG.load()
    dag.add_edge(from_id, to_id, reason=reason, agent_id=agent_id)
    dag.save()
    print(f"[dag-builder] Linked: {from_id} → {to_id}  ({reason})")


def cmd_query(node_id: str, direction: str = "out") -> None:
    dag = MemoryDAG.load()
    if direction == "out":
        edges = dag.get_outgoing(node_id)
        label = "outgoing"
    elif direction == "in":
        edges = dag.get_incoming(node_id)
        label = "incoming"
    else:
        edges_out = dag.get_outgoing(node_id)
        edges_in  = dag.get_incoming(node_id)
        print(f"Node: {node_id}")
        print(f"  Outgoing ({len(edges_out)}):")
        for e in edges_out:
            print(f"    → {e['to']}  ({e['reason']})")
        print(f"  Incoming ({len(edges_in)}):")
        for e in edges_in:
            print(f"    ← {e['from']}  ({e['reason']})")
        return

    print(f"{label.capitalize()} links for {node_id}:")
    if not edges:
        print("  (none)")
    for e in edges:
        print(f"  {'→' if direction == 'out' else '←'} {e.get('to' if direction == 'out' else 'from', '?')}  ({e['reason']})")


def cmd_paths(from_id: str, to_id: str, json_output: bool = False) -> None:
    dag = MemoryDAG.load()
    path = dag.shortest_path(from_id, to_id)
    if json_output:
        print(json.dumps({"from": from_id, "to": to_id, "path": path}, ensure_ascii=False, indent=2))
        return
    if path:
        print(f"Path ({len(path)} hops): " + " → ".join(path))
    else:
        print(f"No path found between {from_id} and {to_id}")


def cmd_neighbors(node_id: str, depth: int = 1) -> None:
    dag = MemoryDAG.load()
    neighbors = dag.get_neighbors(node_id, depth=depth)
    print(f"Neighbors of {node_id} (depth={depth}): {len(neighbors)} found")
    for n in sorted(neighbors):
        print(f"  - {n}")


def cmd_stats() -> None:
    dag = MemoryDAG.load()
    s = dag.stats()
    print(f"DAG stats:")
    print(f"  nodes:        {s['nodes']}")
    print(f"  edges:        {s['edges']}")
    print(f"  avg out-deg:  {s['avg_out_degree']:.3f}")


def main():
    parser = argparse.ArgumentParser(description="Memory DAG Builder (pure Python)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="Build DAG from memory/index.json (auto-link by shared tags)")
    sub.add_parser("stats", help="Show DAG statistics")

    p_link = sub.add_parser("link", help="Manually link two memory entries")
    p_link.add_argument("from_id", help="Source memory ID")
    p_link.add_argument("to_id", help="Target memory ID")
    p_link.add_argument("reason", nargs="?", default="", help="Reason for the link")

    p_query = sub.add_parser("query", help="Query links for a memory entry")
    p_query.add_argument("node_id", help="Memory entry ID")
    p_query.add_argument("--direction", "-d", choices=["in", "out", "both"], default="out")

    p_paths = sub.add_parser("paths", help="Find shortest path between two entries")
    p_paths.add_argument("from_id")
    p_paths.add_argument("to_id")
    p_paths.add_argument("--json", action="store_true")

    p_neighbors = sub.add_parser("neighbors", help="Get neighboring nodes (BFS)")
    p_neighbors.add_argument("node_id")
    p_neighbors.add_argument("--depth", "-n", type=int, default=1)

    args = parser.parse_args()

    if args.cmd == "build":
        cmd_build()
    elif args.cmd == "stats":
        cmd_stats()
    elif args.cmd == "link":
        cmd_link(args.from_id, args.to_id, args.reason)
    elif args.cmd == "query":
        cmd_query(args.node_id, args.direction)
    elif args.cmd == "paths":
        cmd_paths(args.from_id, args.to_id, args.json)
    elif args.cmd == "neighbors":
        cmd_neighbors(args.node_id, args.depth)


if __name__ == "__main__":
    main()
