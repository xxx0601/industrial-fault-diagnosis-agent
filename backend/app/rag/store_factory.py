"""Create vector store — ChromaDB preferred, memory fallback."""

from pathlib import Path
from typing import Any, Protocol

from app.core.config import Settings


class VectorStoreProtocol(Protocol):
    def add_chunks(self, doc_id: str, doc_name: str, chunks: list[str]) -> int: ...
    def delete_by_doc_id(self, doc_id: str) -> None: ...
    def search(self, query: str, top_k: int) -> list[dict[str, Any]]: ...


def create_vector_store(settings: Settings) -> VectorStoreProtocol:
    backend = settings.vector_store_backend.lower()
    if backend in ("chroma", "auto"):
        try:
            from app.rag.chroma_store import ChromaVectorStore

            return ChromaVectorStore(settings)
        except Exception:
            pass
    path = Path(settings.memory_vector_index_path).resolve()
    from app.rag.memory_store import MemoryVectorStore

    return MemoryVectorStore(path)
