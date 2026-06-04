"""Local filesystem storage for uploaded device logs."""

from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings


class FileStorage:
    def __init__(self, settings: Settings) -> None:
        self._root = Path(settings.upload_dir).resolve()
        self._max_bytes = settings.upload_max_bytes

    def ensure_ready(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)

    def stored_path(self, stored_name: str) -> Path:
        return self._root / stored_name

    async def save_upload(
        self,
        upload: UploadFile,
        stored_name: str,
    ) -> tuple[Path, int]:
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

    def read_text(self, stored_name: str, encoding: str = "utf-8") -> str:
        path = self.stored_path(stored_name)
        if not path.is_file():
            raise FileNotFoundError(f"Stored file not found: {stored_name}")
        return path.read_text(encoding=encoding, errors="replace")

    def delete_file(self, stored_name: str) -> None:
        self.stored_path(stored_name).unlink(missing_ok=True)
