#!/usr/bin/env python3
"""
memory-indexer.py — Keyword-based memory indexer for OpenClaw multi-agent system.

Supports:
  --build       Rebuild index from memory/ directory
  --search      Recall relevant memories (keyword match + weight scoring)
  --agent-id    Filter by agent ID (default: current agent workspace)
  --shared      Include shared memories in search (default: true)
  --top N       Return top N results (default: 3)
  --json        Output raw JSON (default: formatted text)

BM25 is used for semantic scoring; results are merged with existing weight scores.

Usage:
  python memory-indexer.py --build
  python memory-indexer.py --search "Vue performance optimization" --agent-id dev
  python memory-indexer.py --search "Docker deployment" --top 5
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────────────

WORKSPACE = Path.home() / ".openclaw" / "workspace-dev"
MEMORY_DIR = WORKSPACE / "memory"
INDEX_FILE = MEMORY_DIR / "index.json"
DAG_DIR    = MEMORY_DIR / "dag"

# Default agent workspace to dev
DEFAULT_AGENT = "dev"

# ─── Index Schema ─────────────────────────────────────────────────────────────
# index.json shape:
# {
#   "version": 2,
#   "built_at": "ISO8601",
#   "entries": [
#     {
#       "id": "sha256_hex",
#       "file": "YYYY-MM-DD.md",          # relative to memory/
#       "path": "/full/path/to/file",
#       "agent_id": "dev",               # source agent workspace
#       "shared": false,                 # cross-agent visibility
#       "tags": ["vue", "performance"],  # extracted or inferred
#       "weight": 0.8,                   # 0.0–1.0, trust/signal strength
#       "p": "P1",                        # P0/P1/P2 TTL class
#       "summary": "...",                # first 200 chars of content
#       "keywords": ["keyword", "list"], # all-lowercase, deduplicated
#       "bm25_doc": ["tokenized", "terms"]
#     }
#   ]
# }

# ─── Helpers ─────────────────────────────────────────────────────────────────

def log(msg: str):
    print(f"[memory-indexer] {msg}", file=sys.stderr)

def compute_id(content: str, path: str) -> str:
    import hashlib
    return hashlib.sha256(f"{path}:{content}".encode()).hexdigest()[:16]

def extract_keywords(text: str) -> list[str]:
    """Pull meaningful tokens from text for keyword index."""
    text = text.lower()
    # strip markdown, code blocks, URLs
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"#+\s*", " ", text)
    # keep alphanumeric words >= 2 chars
    words = re.findall(r"\b[a-z][a-z0-9]{1,}\b", text)
    # stopwords
    stop = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "by","from","as","is","was","are","were","be","been","being","have",
        "has","had","do","does","did","will","would","could","should","may",
        "might","must","shall","can","need","it","its","this","that","these",
        "those","i","we","you","he","she","they","what","which","who","how",
        "when","where","why","not","no","yes","all","any","each","every",
        "some","more","most","other","such","only","same","so","than","too",
        "very","just","also","now","here","there","then","once","if","though",
        "because","until","while","about","after","before","above","below",
        "between","into","through","during","without","within","along",
        "across","behind","beyond","near","off","out","over","under","up",
        "down","back","again","further","once","python","file","path","dir",
        "function","class","method","def","return","import","export","from",
        "module","code","use","using","used","using","see","note","note",
        "default","none","null","true","false","set","get","new","make"
    }
    return [w for w in words if w not in stop and len(w) >= 3]

def infer_p(text: str) -> str:
    """Infer TTL class from content markers."""
    if "P0" in text or "永不过期" in text or "永久" in text:
        return "P0"
    if "P2" in text or "临时" in text or "debug" in text.lower():
        return "P2"
    return "P1"

def extract_summary(content: str, max_chars: int = 200) -> str:
    """First non-empty line or max_chars of content."""
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    for line in lines:
        if not line.startswith("#"):
            return line[:max_chars]
    return (lines[0] or "")[:max_chars] if lines else content[:max_chars]

def infer_shared(file_path: Path, content: str) -> bool:
    """Infer shared=True from path or content markers."""
    name = file_path.name.lower()
    if name.startswith("daydream") or name.startswith("meditation"):
        return True
    if "shared" in content.lower()[:500]:
        return True
    return False

# ─── Build ───────────────────────────────────────────────────────────────────

def build_index(agent_id: str = DEFAULT_AGENT) -> dict:
    """Walk memory/ and rebuild the index."""
    log(f"Building index (agent={agent_id})...")
    start = time.monotonic()

    entries = []
    seen_ids = set()

    # Walk all markdown files in memory/
    if not MEMORY_DIR.exists():
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(MEMORY_DIR.rglob("*.md")):
        rel = md_file.relative_to(MEMORY_DIR)
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            log(f"  [WARN] Cannot read {md_file}: {e}")
            continue

        file_id  = compute_id(content, str(md_file))
        keywords = extract_keywords(content)
        summary  = extract_summary(content)
        p        = infer_p(content)
        shared   = infer_shared(md_file, content)
        tags     = keywords[:10]  # top keywords as tags

        entry = {
            "id":        file_id,
            "file":      str(rel),
            "path":      str(md_file),
            "agent_id":  agent_id,
            "shared":    shared,
            "tags":      tags,
            "weight":    0.5,
            "p":         p,
            "summary":   summary,
            "keywords":  keywords,
            "bm25_doc":  keywords,  # pre-tokenized for bm25_search
        }
        entries.append(entry)

    index = {
        "version":  2,
        "built_at": __import__("datetime").datetime.now().isoformat(),
        "agent_id": agent_id,
        "entries":  entries,
    }

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    elapsed = (time.monotonic() - start) * 1000
    log(f"Indexed {len(entries)} files in {elapsed:.1f}ms → {INDEX_FILE}")
    return index


# ─── Search ──────────────────────────────────────────────────────────────────

def search(
    query: str,
    agent_id: str = DEFAULT_AGENT,
    include_shared: bool = True,
    top_n: int = 3,
    json_output: bool = False,
) -> list[dict]:
    """Keyword + BM25 hybrid search over memory index.

    Scoring: combined_score = bm25_norm * 0.6 + weight * 0.4
    Filter:  (entry["agent_id"] == agent_id) OR (entry["shared"] == true)
    """

    if not INDEX_FILE.exists():
        log("Index not found. Running --build first...")
        build_index(agent_id)

    with open(INDEX_FILE, encoding="utf-8") as f:
        index = json.load(f)

    query_tokens = extract_keywords(query)
    if not query_tokens:
        query_tokens = query.lower().split()

    results: list[tuple[float, dict]] = []

    for entry in index.get("entries", []):
        # Filter: must match agent_id OR be shared
        if entry["agent_id"] != agent_id and not entry.get("shared", False):
            continue

        # BM25 scoring using in-memory corpus
        entry_tokens = entry.get("bm25_doc", entry.get("keywords", []))
        bm25_score = bm25_score_single(query_tokens, entry_tokens)

        # Weight scoring
        weight_score = entry.get("weight", 0.5)

        # Keyword overlap bonus
        q_set = set(query_tokens)
        e_set = set(entry_tokens)
        overlap = len(q_set & e_set) / max(len(q_set), 1)
        overlap_bonus = overlap * 0.2  # up to +0.2 for exact keyword overlap

        combined = (bm25_score * 0.6) + (weight_score * 0.2) + overlap_bonus

        results.append((combined, entry))

    results.sort(key=lambda x: x[0], reverse=True)
    top = [r for _, r in results[:top_n]]

    if json_output:
        return top

    if not top:
        print(f"[memory-indexer] No results for: {query}")
        return []

    print(f"[memory-indexer] Top {len(top)} results for: {query}")
    print("-" * 60)
    for i, entry in enumerate(top, 1):
        score = results[i-1][0] if i-1 < len(results) else 0
        print(f"  [{i}] {entry['file']}  score={score:.3f}  weight={entry['weight']}  shared={entry.get('shared', False)}")
        print(f"      {entry['summary']}")
        print()
    return top


def bm25_score_single(query_tokens: list[str], doc_tokens: list[str]) -> float:
    """
    Okapi BM25 scoring for a single document.
    Pure Python, no external deps.
    """
    if not query_tokens or not doc_tokens:
        return 0.0

    N = 1  # number of documents (single doc mode)
    avgdl = len(doc_tokens)  # approximate
    k1 = 1.5
    b = 0.75

    doc_tf = defaultdict(int)
    for t in doc_tokens:
        doc_tf[t] += 1

    score = 0.0
    dl = len(doc_tokens)

    for term in query_tokens:
        tf = doc_tf.get(term, 0)
        if tf == 0:
            continue
        # idf: use log((N - n + 0.5) / (n + 0.5) + 1), approximated as log(2)
        idf = 0.693  # natural log, since n=0 (term not in corpus)
        term_freq_component = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / max(avgdl, 1)))
        score += idf * term_freq_component

    # Normalize to 0–1 (rough): max possible per query length
    max_possible = len(query_tokens) * (k1 + 1) / k1
    return min(score / max(max_possible, 1), 1.0)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    # Inspect first arg to choose mode
    if len(sys.argv) > 1 and sys.argv[1] in ("build", "search"):
        # Subcommand mode
        sub = argparse.ArgumentParser(description="OpenClaw Memory Indexer")
        sub.add_argument("cmd", choices=["build", "search"])
        sub.add_argument("--agent-id", default=DEFAULT_AGENT)
        sub.add_argument("--top", type=int, default=3)
        sub.add_argument("--json", action="store_true")
        sub.add_argument("--shared", dest="shared", action="store_true", default=True)
        sub.add_argument("--no-shared", dest="shared", action="store_false")
        if sys.argv[1] == "search":
            sub.add_argument("query", nargs="+", help="Search keywords")
        sub_args = sub.parse_args()
        if sub_args.cmd == "build":
            build_index(sub_args.agent_id)
        else:
            search(" ".join(sub_args.query), sub_args.agent_id,
                   sub_args.shared, sub_args.top, sub_args.json)
    else:
        # Flat flag mode (backward compatible)
        parser = argparse.ArgumentParser(description="OpenClaw Memory Indexer")
        parser.add_argument("--build", dest="cmd_build", action="store_true")
        parser.add_argument("--search", dest="cmd_search", nargs="*", default=None)
        parser.add_argument("--agent-id", dest="agent_id", default=DEFAULT_AGENT)
        parser.add_argument("--shared", dest="shared", action="store_true", default=True)
        parser.add_argument("--no-shared", dest="shared", action="store_false")
        parser.add_argument("--top", type=int, dest="top_n", default=3)
        parser.add_argument("--json", dest="json", action="store_true")
        args = parser.parse_args()
        if args.cmd_build:
            build_index(args.agent_id)
        elif args.cmd_search is not None:
            search(" ".join(args.cmd_search), args.agent_id,
                   args.shared, args.top_n, args.json)
        else:
            parser.print_help()
            sys.exit(1)

if __name__ == "__main__":
    main()
