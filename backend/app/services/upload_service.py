"""Upload business logic — shared by API and future Fault Diagnosis Agent."""

import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.models.upload_record import UploadRecord
from app.repositories.upload_repo import UploadRepository
from app.schemas.upload import UploadResponse
from app.storage.file_storage import FileStorage

ALLOWED_EXTENSIONS = frozenset({"txt", "csv", "json"})


class UploadService:
    def __init__(
        self,
        settings: Settings,
        storage: FileStorage,
        repo: UploadRepository,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._repo = repo

    def ensure_ready(self) -> None:
        self._storage.ensure_ready()
        self._repo.ensure_ready()

    def list_uploads(self) -> list[UploadResponse]:
        return [self._to_response(record) for record in self._repo.list_all()]

    async def create_upload(self, upload: UploadFile) -> UploadResponse:
        if not upload.filename:
            raise ValidationError("Filename is required")

        file_type = self._resolve_file_type(upload.filename)
        file_id = str(uuid.uuid4())
        stored_name = f"{file_id}.{file_type}"
        upload_time = datetime.now(UTC)

        try:
            _, size_bytes = await self._storage.save_upload(upload, stored_name)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        finally:
            await upload.close()

        record = UploadRecord(
            file_id=file_id,
            filename=upload.filename,
            file_type=file_type,
            upload_time=upload_time,
            stored_name=stored_name,
            size_bytes=size_bytes,
            content_type=upload.content_type,
        )
        self._repo.add(record)
        return self._to_response(record)

    def get_record(self, file_id: str) -> UploadRecord:
        record = self._repo.get(file_id)
        if record is None:
            raise NotFoundError(f"Upload not found: {file_id}")
        return record

    def read_log_content(self, file_id: str) -> str:
        """Entry point for Agent / RAG / diagnosis — read raw log text by file_id."""
        record = self.get_record(file_id)
        return self._storage.read_text(record.stored_name)

    def resolve_stored_path(self, file_id: str) -> Path:
        """Return on-disk path when Agent tools need direct file access."""
        record = self.get_record(file_id)
        return self._storage.stored_path(record.stored_name)

    def _resolve_file_type(self, filename: str) -> str:
        ext = Path(filename).suffix.lower().lstrip(".")
        allowed = self._settings.allowed_extension_set or ALLOWED_EXTENSIONS
        if ext not in allowed:
            raise ValidationError(
                f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(allowed))}"
            )
        return ext

    @staticmethod
    def _to_response(record: UploadRecord) -> UploadResponse:
        return UploadResponse(
            file_id=record.file_id,
            filename=record.filename,
            file_type=record.file_type,
            upload_time=record.upload_time,
        )


def build_upload_service(settings: Settings) -> UploadService:
    storage = FileStorage(settings)
    repo = UploadRepository(Path(settings.upload_index_path).resolve())
    return UploadService(settings, storage, repo)
