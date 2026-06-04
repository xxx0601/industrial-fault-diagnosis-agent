"""Knowledge base API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeUploadResponse(BaseModel):
    doc_id: str
    doc_name: str
    status: str
    upload_time: datetime
    chunk_count: int = 0


class KnowledgeDocumentSummary(BaseModel):
    doc_id: str
    doc_name: str
    description: str | None = None
    filename: str
    status: str
    chunk_count: int
    upload_time: datetime


class KnowledgeDocumentListResponse(BaseModel):
    items: list[KnowledgeDocumentSummary] = Field(default_factory=list)
    total: int = 0


class KnowledgeSearchHit(BaseModel):
    doc_id: str
    doc_name: str | None = None
    chunk_text: str
    similarity_score: float
    chunk_index: int | None = None


class KnowledgeSearchResponse(BaseModel):
    query: str
    hits: list[KnowledgeSearchHit] = Field(default_factory=list)
    total: int = 0


class KnowledgeDeleteResponse(BaseModel):
    doc_id: str
    deleted: bool
    message: str
