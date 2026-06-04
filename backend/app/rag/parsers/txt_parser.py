"""Plain text document parser."""

from app.rag.parsers.base import DocumentParser


class TxtParser:
    @property
    def supported_extensions(self) -> set[str]:
        return {"txt"}

    def parse_bytes(self, data: bytes) -> str:
        for encoding in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
            try:
                return data.decode(encoding).strip()
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace").strip()
