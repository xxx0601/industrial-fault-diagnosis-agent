"""Persist uploaded knowledge documents (PDF, future DOCX/TXT)."""

from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings


class KnowledgeStorage:
    def __init__(self, settings: Settings) -> None:
        self._root = Path(settings.knowledge_files_dir).resolve()
        self._max_bytes = settings.knowledge_max_bytes

    def ensure_ready(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)

    def stored_path(self, stored_name: str) -> Path:
        return self._root / stored_name

    async def save_file(self, upload: UploadFile, stored_name: str) -> tuple[Path, int]:
        dest = self.stored_path(stored_name)
        size = 0
        chunk_size = 1024 * 1024
        with dest.open("wb") as out:
            while True:
                chunk = await upload.read(chunk_size)
                if not chunk:
                    break
                size += len(chunk)
                if size > self._max_bytes:
                    dest.unlink(missing_ok=True)
                    raise ValueError(
                        f"File exceeds maximum size of {self._max_bytes} bytes"
                    )
                out.write(chunk)
        return dest, size

    def delete_file(self, stored_name: str) -> None:
        self.stored_path(stored_name).unlink(missing_ok=True)
