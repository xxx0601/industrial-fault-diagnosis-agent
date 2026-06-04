"""Upload metadata persistence — JSON index now, PostgreSQL later."""

import json
from datetime import datetime
from pathlib import Path

from app.models.upload_record import UploadRecord


class UploadRepository:
    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path

    def ensure_ready(self) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._index_path.write_text("[]", encoding="utf-8")

    def list_all(self) -> list[UploadRecord]:
        return sorted(
            [self._from_dict(item) for item in self._read_raw()],
            key=lambda r: r.upload_time,
            reverse=True,
        )

    def get(self, file_id: str) -> UploadRecord | None:
        for record in self.list_all():
            if record.file_id == file_id:
                return record
        return None

    def add(self, record: UploadRecord) -> UploadRecord:
        items = self._read_raw()
        if any(item["file_id"] == record.file_id for item in items):
            raise ValueError(f"Duplicate file_id: {record.file_id}")
        items.append(self._to_dict(record))
        self._write_raw(items)
        return record

    def _read_raw(self) -> list[dict]:
        self.ensure_ready()
        data = json.loads(self._index_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Upload index must be a JSON array")
        return data

    def _write_raw(self, items: list[dict]) -> None:
        self._index_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _to_dict(record: UploadRecord) -> dict:
        return {
            "file_id": record.file_id,
            "filename": record.filename,
            "file_type": record.file_type,
            "upload_time": record.upload_time.isoformat(),
            "stored_name": record.stored_name,
            "size_bytes": record.size_bytes,
            "content_type": record.content_type,
        }

    @staticmethod
    def _from_dict(data: dict) -> UploadRecord:
        return UploadRecord(
            file_id=data["file_id"],
            filename=data["filename"],
            file_type=data["file_type"],
            upload_time=datetime.fromisoformat(data["upload_time"]),
            stored_name=data["stored_name"],
            size_bytes=int(data["size_bytes"]),
            content_type=data.get("content_type"),
        )
