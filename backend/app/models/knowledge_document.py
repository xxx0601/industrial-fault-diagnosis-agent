"""Domain model for knowledge base documents."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class KnowledgeDocument:
    doc_id: str
    doc_name: str
    description: str | None
    filename: str
    stored_name: str
    status: str
    chunk_count: int
    upload_time: datetime
