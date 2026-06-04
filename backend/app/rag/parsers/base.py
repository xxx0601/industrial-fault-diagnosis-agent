"""Document parser protocol — extend for DOCX, TXT in future steps."""

from typing import Protocol


class DocumentParser(Protocol):
    @property
    def supported_extensions(self) -> set[str]:
        ...

    def parse_bytes(self, data: bytes) -> str:
        """Extract plain text from raw file bytes."""
