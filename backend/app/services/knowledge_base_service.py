"""Knowledge base orchestration — upload, index, search."""

import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.models.knowledge_document import KnowledgeDocument
from app.rag.ingest import DocumentIngestor
from app.rag.retriever import KnowledgeRetriever
from app.rag.store_factory import VectorStoreProtocol, create_vector_store
from app.repositories.knowledge_repo import KnowledgeRepository
from app.schemas.knowledge import (
    KnowledgeDocumentListResponse,
    KnowledgeDocumentSummary,
    KnowledgeSearchHit,
    KnowledgeDeleteResponse,
    KnowledgeSearchResponse,
    KnowledgeUploadResponse,
)
from app.storage.knowledge_storage import KnowledgeStorage

STATUS_INDEXED = "indexed"
STATUS_FAILED = "failed"


class KnowledgeBaseService:
    def __init__(
        self,
        settings: Settings,
        storage: KnowledgeStorage,
        repo: KnowledgeRepository,
        ingestor: DocumentIngestor,
        retriever: KnowledgeRetriever,
        vector_store: VectorStoreProtocol,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._repo = repo
        self._ingestor = ingestor
        self._retriever = retriever
        self._vector_store = vector_store

    def ensure_ready(self) -> None:
        self._storage.ensure_ready()
        self._repo.ensure_ready()

    async def upload_document(
        self,
        file: UploadFile,
        doc_name: str,
        description: str | None = None,
    ) -> KnowledgeUploadResponse:
        if not file.filename:
            raise ValidationError("Filename is required")

        ext = Path(file.filename).suffix.lower().lstrip(".")
        allowed = self._settings.knowledge_extension_set
        if ext not in allowed:
            raise ValidationError(
                f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(allowed))}"
            )

        name = doc_name.strip() or Path(file.filename).stem
        doc_id = str(uuid.uuid4())
        stored_name = f"{doc_id}.{ext}"
        upload_time = datetime.now(UTC)

        try:
            path, _size = await self._storage.save_file(file, stored_name)
            data = path.read_bytes()
            chunk_count, _text = self._ingestor.ingest_document_bytes(
                doc_id, name, data, ext
            )
            status = STATUS_INDEXED
        except Exception as exc:
            self._storage.stored_path(stored_name).unlink(missing_ok=True)
            raise ValidationError(f"Ingest failed: {exc}") from exc
        finally:
            await file.close()

        record = KnowledgeDocument(
            doc_id=doc_id,
            doc_name=name,
            description=description,
            filename=file.filename,
            stored_name=stored_name,
            status=status,
            chunk_count=chunk_count,
            upload_time=upload_time,
        )
        self._repo.add(record)

        return KnowledgeUploadResponse(
            doc_id=doc_id,
            doc_name=name,
            status=status,
            upload_time=upload_time,
            chunk_count=chunk_count,
        )

    async def upload_pdf(
        self,
        file: UploadFile,
        doc_name: str,
        description: str | None = None,
    ) -> KnowledgeUploadResponse:
        """Backward-compatible alias."""
        return await self.upload_document(file, doc_name, description)

    def list_documents(self) -> KnowledgeDocumentListResponse:
        items = [
            KnowledgeDocumentSummary(
                doc_id=d.doc_id,
                doc_name=d.doc_name,
                description=d.description,
                filename=d.filename,
                status=d.status,
                chunk_count=d.chunk_count,
                upload_time=d.upload_time,
            )
            for d in self._repo.list_all()
        ]
        return KnowledgeDocumentListResponse(items=items, total=len(items))

    def search(self, query: str, top_k: int | None = None) -> KnowledgeSearchResponse:
        if not query.strip():
            raise ValidationError("Query is required")
        k = top_k or self._settings.rag_default_top_k
        hits = self._retriever.search(query, k)
        return KnowledgeSearchResponse(query=query, hits=hits, total=len(hits))

    def get_document(self, doc_id: str) -> KnowledgeDocument:
        doc = self._repo.get(doc_id)
        if doc is None:
            raise NotFoundError(f"Document not found: {doc_id}")
        return doc

    def delete_document(self, doc_id: str) -> KnowledgeDeleteResponse:
        doc = self._repo.get(doc_id)
        if doc is None:
            raise NotFoundError(f"Document not found: {doc_id}")

        self._vector_store.delete_by_doc_id(doc_id)
        self._storage.delete_file(doc.stored_name)
        self._repo.delete(doc_id)

        return KnowledgeDeleteResponse(
            doc_id=doc_id,
            deleted=True,
            message=f"已删除文档：{doc.doc_name}",
        )


def build_knowledge_base_service(settings: Settings) -> KnowledgeBaseService:
    storage = KnowledgeStorage(settings)
    repo = KnowledgeRepository(Path(settings.knowledge_index_path).resolve())
    store = create_vector_store(settings)
    ingestor = DocumentIngestor(settings, store)
    retriever = KnowledgeRetriever(store)
    return KnowledgeBaseService(settings, storage, repo, ingestor, retriever, store)
