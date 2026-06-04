"""ChromaDB vector store wrapper."""

from pathlib import Path
from typing import Any
from uuid import uuid4

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import Settings


class ChromaVectorStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        persist = Path(settings.chroma_persist_dir).resolve()
        persist.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist))
        self._collection_name = settings.chroma_collection

    @property
    def collection(self) -> Collection:
        return self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"project": "industrial_fault_diagnosis"},
        )

    def add_chunks(
        self,
        doc_id: str,
        doc_name: str,
        chunks: list[str],
        source_type: str = "pdf",
    ) -> int:
        if not chunks:
            return 0
        col = self.collection
        ids = [f"{doc_id}:{i}:{uuid4().hex[:8]}" for i in range(len(chunks))]
        metadatas = [
            {
                "doc_id": doc_id,
                "doc_name": doc_name,
                "chunk_index": i,
                "source_type": source_type,
            }
            for i in range(len(chunks))
        ]
        col.add(ids=ids, documents=chunks, metadatas=metadatas)
        return len(chunks)

    def delete_by_doc_id(self, doc_id: str) -> None:
        col = self.collection
        try:
            col.delete(where={"doc_id": doc_id})
        except Exception:
            pass

    def search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        col = self.collection
        if col.count() == 0:
            return []
        result = col.query(query_texts=[query], n_results=top_k)
        hits: list[dict[str, Any]] = []
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        for doc_text, meta, dist in zip(docs, metas, distances):
            if not doc_text:
                continue
            score = 1.0 / (1.0 + float(dist)) if dist is not None else 0.0
            hits.append(
                {
                    "doc_id": meta.get("doc_id", ""),
                    "doc_name": meta.get("doc_name"),
                    "chunk_text": doc_text,
                    "similarity_score": round(score, 4),
                    "chunk_index": meta.get("chunk_index"),
                }
            )
        return hits
