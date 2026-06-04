"""Ingest pipeline: parse document → chunk → vector store."""

from app.core.config import Settings
from app.rag.chunking import chunk_text
from app.rag.parsers.pdf_parser import PdfParser
from app.rag.parsers.txt_parser import TxtParser
from app.rag.store_factory import VectorStoreProtocol

_SUPPORTED = {
    "pdf": PdfParser(),
    "txt": TxtParser(),
}


class DocumentIngestor:
    def __init__(self, settings: Settings, store: VectorStoreProtocol) -> None:
        self._settings = settings
        self._store = store

    def ingest_document_bytes(
        self,
        doc_id: str,
        doc_name: str,
        data: bytes,
        file_type: str,
    ) -> tuple[int, str]:
        ext = file_type.lower().lstrip(".")
        parser = _SUPPORTED.get(ext)
        if parser is None:
            raise ValueError(
                f"Unsupported knowledge file type: .{ext}. "
                f"Allowed: {', '.join(sorted(_SUPPORTED))}"
            )

        text = parser.parse_bytes(data)
        if not text.strip():
            raise ValueError(f".{ext} file contains no extractable text")

        chunks = chunk_text(
            text,
            chunk_size=self._settings.rag_chunk_size,
            chunk_overlap=self._settings.rag_chunk_overlap,
        )
        self._store.delete_by_doc_id(doc_id)
        count = self._store.add_chunks(doc_id, doc_name, chunks, source_type=ext)
        return count, text

    def ingest_pdf_bytes(
        self,
        doc_id: str,
        doc_name: str,
        data: bytes,
    ) -> tuple[int, str]:
        """Backward-compatible alias."""
        return self.ingest_document_bytes(doc_id, doc_name, data, "pdf")
