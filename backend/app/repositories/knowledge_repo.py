"""Knowledge document metadata — JSON index, PostgreSQL later."""

import json
from datetime import datetime
from pathlib import Path

from app.models.knowledge_document import KnowledgeDocument


class KnowledgeRepository:
    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path

    def ensure_ready(self) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._index_path.write_text("[]", encoding="utf-8")

    def add(self, document: KnowledgeDocument) -> KnowledgeDocument:
        items = self._read_raw()
        items.append(self._to_dict(document))
        self._write_raw(items)
        return document

    def get(self, doc_id: str) -> KnowledgeDocument | None:
        for doc in self.list_all():
            if doc.doc_id == doc_id:
                return doc
        return None

    def delete(self, doc_id: str) -> bool:
        items = self._read_raw()
        new_items = [item for item in items if item.get("doc_id") != doc_id]
        if len(new_items) == len(items):
            return False
        self._write_raw(new_items)
        return True

    def list_all(self) -> list[KnowledgeDocument]:
        return sorted(
            [self._from_dict(item) for item in self._read_raw()],
            key=lambda d: d.upload_time,
            reverse=True,
        )

    def _read_raw(self) -> list[dict]:
        self.ensure_ready()
        data = json.loads(self._index_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Knowledge index must be a JSON array")
        return data

    def _write_raw(self, items: list[dict]) -> None:
        self._index_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _to_dict(doc: KnowledgeDocument) -> dict:
        return {
            "doc_id": doc.doc_id,
            "doc_name": doc.doc_name,
            "description": doc.description,
            "filename": doc.filename,
            "stored_name": doc.stored_name,
            "status": doc.status,
            "chunk_count": doc.chunk_count,
            "upload_time": doc.upload_time.isoformat(),
        }

    @staticmethod
    def _from_dict(data: dict) -> KnowledgeDocument:
        return KnowledgeDocument(
            doc_id=data["doc_id"],
            doc_name=data["doc_name"],
            description=data.get("description"),
            filename=data["filename"],
            stored_name=data["stored_name"],
            status=data["status"],
            chunk_count=int(data.get("chunk_count", 0)),
            upload_time=datetime.fromisoformat(data["upload_time"]),
        )
