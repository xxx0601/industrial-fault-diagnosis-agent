"""In-memory vector store fallback when ChromaDB is unavailable."""

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any
from uuid import uuid4

import json

_TOKEN_RE = re.compile(r"[a-zA-Z0-9\u4e00-\u9fff]+")


def _tokenize(text: str) -> Counter[str]:
    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    return Counter(tokens)


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a[t] * b[t] for t in a if t in b)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class MemoryVectorStore:
    """JSON-persisted chunk index with bag-of-words similarity."""

    def __init__(self, persist_path: Path) -> None:
        self._path = persist_path
        self._chunks: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if self._path.exists():
            self._chunks = json.loads(self._path.read_text(encoding="utf-8"))
        else:
            self._chunks = []

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._chunks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_chunks(
        self,
        doc_id: str,
        doc_name: str,
        chunks: list[str],
        source_type: str = "pdf",
    ) -> int:
        self.delete_by_doc_id(doc_id)
        for i, text in enumerate(chunks):
            self._chunks.append(
                {
                    "id": f"{doc_id}:{i}:{uuid4().hex[:8]}",
                    "doc_id": doc_id,
                    "doc_name": doc_name,
                    "chunk_index": i,
                    "source_type": source_type,
                    "text": text,
                    "tokens": dict(_tokenize(text)),
                }
            )
        self._save()
        return len(chunks)

    def delete_by_doc_id(self, doc_id: str) -> None:
        self._chunks = [c for c in self._chunks if c.get("doc_id") != doc_id]
        self._save()

    def search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        q = _tokenize(query)
        scored: list[tuple[float, dict[str, Any]]] = []
        for chunk in self._chunks:
            tokens = Counter(chunk.get("tokens") or {})
            score = _cosine(q, tokens)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        hits: list[dict[str, Any]] = []
        for score, chunk in scored[:top_k]:
            hits.append(
                {
                    "doc_id": chunk["doc_id"],
                    "doc_name": chunk.get("doc_name"),
                    "chunk_text": chunk["text"],
                    "similarity_score": round(score, 4),
                    "chunk_index": chunk.get("chunk_index"),
                }
            )
        return hits
