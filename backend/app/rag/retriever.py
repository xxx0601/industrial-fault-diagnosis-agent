"""RAG retriever — query ChromaDB knowledge collection."""

from app.rag.store_factory import VectorStoreProtocol
from app.schemas.knowledge import KnowledgeSearchHit


class KnowledgeRetriever:
    def __init__(self, store: VectorStoreProtocol) -> None:
        self._store = store

    def search(self, query: str, top_k: int) -> list[KnowledgeSearchHit]:
        raw_hits = self._store.search(query, top_k)
        return [
            KnowledgeSearchHit(
                doc_id=h["doc_id"],
                doc_name=h.get("doc_name"),
                chunk_text=h["chunk_text"],
                similarity_score=float(h["similarity_score"]),
                chunk_index=h.get("chunk_index"),
            )
            for h in raw_hits
        ]
