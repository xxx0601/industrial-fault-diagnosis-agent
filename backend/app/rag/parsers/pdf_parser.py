"""PDF text extraction via pypdf."""

import io

from pypdf import PdfReader

from app.rag.parsers.base import DocumentParser


class PdfParser:
    @property
    def supported_extensions(self) -> set[str]:
        return {"pdf"}

    def parse_bytes(self, data: bytes) -> str:
        reader = PdfReader(io.BytesIO(data))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)
        return "\n\n".join(pages).strip()
