from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.api.deps import get_knowledge_base_service
from app.schemas.knowledge import (
    KnowledgeDeleteResponse,
    KnowledgeDocumentListResponse,
    KnowledgeSearchResponse,
    KnowledgeUploadResponse,
)
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge")


@router.post("/upload", response_model=KnowledgeUploadResponse)
async def upload_knowledge_document(
    file: UploadFile = File(..., description="Knowledge document (PDF or TXT)"),
    doc_name: str = Form(..., description="Document display name"),
    description: str | None = Form(default=None),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> KnowledgeUploadResponse:
    return await service.upload_document(file, doc_name, description)


@router.get("/documents", response_model=KnowledgeDocumentListResponse)
def list_knowledge_documents(
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> KnowledgeDocumentListResponse:
    return service.list_documents()


@router.delete("/documents/{doc_id}", response_model=KnowledgeDeleteResponse)
def delete_knowledge_document(
    doc_id: str,
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> KnowledgeDeleteResponse:
    return service.delete_document(doc_id)


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    query: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> KnowledgeSearchResponse:
    return service.search(query, top_k)
