#!/usr/bin/env python3
"""
bm25_search.py — Pure-Python Okapi BM25 implementation for OpenClaw memory search.

No external dependencies. Tokenization matches memory-indexer.py.

Usage:
  python bm25_search.py --build              # Build BM25 index from memory/
  python bm25_search.py --search "query"     # Search (uses existing index)
  python bm25_search.py --search "query" --top 5 --json
"""

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# ─── Config ──────────────────────────────────────────────────────────────────

WORKSPACE  = Path.home() / ".openclaw" / "workspace-dev"
MEMORY_DIR = WORKSPACE / "memory"
INDEX_FILE  = MEMORY_DIR / "index.json"
BM25_INDEX = MEMORY_DIR / "bm25_index.json"

# BM25 parameters
K1 = 1.5
B  = 0.75

# ─── Tokenizer ───────────────────────────────────────────────────────────────

STOP = {
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
    "down","back","again","further"
}

def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"#+\s*", " ", text)
    words = re.findall(r"\b[a-z][a-z0-9]{1,}\b", text)
    return [w for w in words if w not in STOP and len(w) >= 3]


# ─── BM25 Core ───────────────────────────────────────────────────────────────

class BM25Index:
    """
    In-memory BM25 index. Stores:
      - corpus: list of tokenized documents
      - doc_ids: list of entry ids (maps index position → entry id)
      - doc_len: average document length
      - idf: dict term → IDF score
    """

    def __init__(self):
        self.corpus:  list[list[str]] = []
        self.doc_ids: list[str]       = []
        self.doc_lens: list[int]       = []
        self.avgdl:   float            = 0.0
        self.idf:     dict[str, float] = {}

    @classmethod
    def from_index(cls, index_file: Path = INDEX_FILE) -> "BM25Index":
        """Build BM25 index from memory/index.json."""
        with open(index_file, encoding="utf-8") as f:
            index = json.load(f)

        bm = cls()
        for entry in index.get("entries", []):
            # Use pre-tokenized bm25_doc if available
            tokens = entry.get("bm25_doc", entry.get("keywords", []))
            if isinstance(tokens, str):
                tokens = tokens.split()
            bm.corpus.append(tokens)
            bm.doc_ids.append(entry["id"])
            bm.doc_lens.append(len(tokens))

        if bm.corpus:
            bm.avgdl = sum(bm.doc_lens) / len(bm.doc_lens)
            bm._compute_idf()
        return bm

    def _compute_idf(self):
        """Compute IDF for all terms across the corpus."""
        N = len(self.corpus)
        df = defaultdict(int)  # document frequency
        for doc in self.corpus:
            for term in set(doc):
                df[term] += 1

        for term, n in df.items():
            # Smoothed IDF: log((N - n + 0.5) / (n + 0.5) + 1)
            self.idf[term] = math.log((N - n + 0.5) / (n + 0.5) + 1)

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        """Return BM25 score for each document given query tokens."""
        scores = []
        for i, doc in enumerate(self.corpus):
            dl = self.doc_lens[i]
            tf = defaultdict(int)
            for t in doc:
                tf[t] += 1

            score = 0.0
            for term in query_tokens:
                f = tf.get(term, 0)
                if f == 0:
                    continue
                idf = self.idf.get(term, 0)
                numerator = f * (K1 + 1)
                denominator = f + K1 * (1 - B + B * dl / max(self.avgdl, 1))
                score += idf * (numerator / max(denominator, 1e-9))
            scores.append(score)
        return scores

    def search(self, query: str, top_n: int = 3) -> list[tuple[str, float]]:
        """Search query string, return top N (doc_id, score) pairs."""
        tokens = tokenize(query)
        scores = self.get_scores(tokens)

        # Normalize scores to 0–1
        max_score = max(scores) if scores and max(scores) > 0 else 1.0
        norm_scores = [s / max_score for s in scores]

        ranked = sorted(
            [(self.doc_ids[i], norm_scores[i]) for i in range(len(scores)) if scores[i] > 0],
            key=lambda x: x[1],
            reverse=True
        )
        return ranked[:top_n]


# ─── Build ───────────────────────────────────────────────────────────────────

def build_bm25_index(agent_id: str = "dev") -> BM25Index:
    """Build or rebuild BM25 index from memory/index.json."""
    import importlib.util, sys
    script_dir = Path(__file__).parent.resolve()
    spec = importlib.util.spec_from_file_location("memory_indexer", script_dir / "memory-indexer.py")
    memory_indexer = importlib.util.module_from_spec(spec)
    sys.modules["memory_indexer"] = memory_indexer
    spec.loader.exec_module(memory_indexer)

    # Ensure keyword index exists
    if not INDEX_FILE.exists():
        print("[bm25] index.json not found, building keyword index first...", file=sys.stderr)
        memory_indexer.build_index(agent_id)

    bm = BM25Index.from_index(INDEX_FILE)
    data = {
        "version":  2,
        "built_at": __import__("datetime").datetime.now().isoformat(),
        "doc_ids":  bm.doc_ids,
        "avgdl":    bm.avgdl,
        "idf":      bm.idf,
        "corpus":   bm.corpus,
    }
    BM25_INDEX.parent.mkdir(parents=True, exist_ok=True)
    BM25_INDEX.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"[bm25] Built index: {len(bm.corpus)} docs, avgdl={bm.avgdl:.1f}", file=sys.stderr)
    return bm


def load_bm25_index() -> Optional["BM25Index"]:
    """Load existing BM25 index or return None."""
    if not BM25_INDEX.exists():
        return None
    try:
        with open(BM25_INDEX, encoding="utf-8") as f:
            data = json.load(f)
        bm = BM25Index()
        bm.corpus  = data["corpus"]
        bm.doc_ids = data["doc_ids"]
        bm.avgdl   = data["avgdl"]
        bm.idf     = data["idf"]
        bm.doc_lens = [len(d) for d in bm.corpus]
        return bm
    except Exception as e:
        print(f"[bm25] Failed to load BM25 index: {e}", file=sys.stderr)
        return None


def search(
    query: str,
    agent_id: str = "dev",
    include_shared: bool = True,
    top_n: int = 3,
    json_output: bool = False,
):
    """Hybrid search: BM25 + weight scoring over memory entries."""
    bm = load_bm25_index()
    if bm is None:
        print("[bm25] No BM25 index found. Run --build first.", file=sys.stderr)
        sys.exit(1)

    # Load full index to get entry details
    with open(INDEX_FILE, encoding="utf-8") as f:
        index = json.load(f)

    entry_map = {e["id"]: e for e in index.get("entries", [])}
    bm_scores = bm.search(query, top_n=top_n * 3)  # over-fetch for filtering

    results = []
    for doc_id, bm_score in bm_scores:
        entry = entry_map.get(doc_id)
        if not entry:
            continue
        # Filter
        if entry["agent_id"] != agent_id and not entry.get("shared", False):
            continue
        weight   = entry.get("weight", 0.5)
        combined = bm_score * 0.6 + weight * 0.4
        results.append((combined, bm_score, entry))

    results.sort(key=lambda x: x[0], reverse=True)
    top = results[:top_n]

    if json_output:
        out = [{"id": e["id"], "file": e["file"], "summary": e["summary"],
                "bm25": s, "combined": c, "weight": e.get("weight"),
                "shared": e.get("shared"), "tags": e.get("tags", [])}
               for c, s, e in top]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return out

    if not top:
        print(f"[bm25] No results for: {query}")
        return []

    print(f"[bm25] Top {len(top)} results for: {query}")
    print("-" * 60)
    for combined, bm_score, entry in top:
        print(f"  {entry['file']}  bm25={bm_score:.3f} combined={combined:.3f} shared={entry.get('shared')}")
        print(f"    {entry['summary']}")
        print()
    return top


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BM25 Memory Search (pure Python)")
    parser.add_argument("--build", action="store_true", help="Build BM25 index")
    parser.add_argument("--search", nargs="*", help="Search query")
    parser.add_argument("--agent-id", default="dev")
    parser.add_argument("--no-shared", dest="shared", action="store_false", default=True)
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.build:
        build_bm25_index(args.agent_id)
    elif args.search is not None:
        query = " ".join(args.search)
        search(query, args.agent_id, args.shared, args.top, args.json)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
