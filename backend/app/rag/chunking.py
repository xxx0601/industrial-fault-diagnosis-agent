"""Recursive character chunking for knowledge documents."""


def chunk_text(
    text: str,
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[str]:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    length = len(normalized)
    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            split_at = normalized.rfind("\n", start, end)
            if split_at == -1 or split_at <= start:
                split_at = normalized.rfind(" ", start, end)
            if split_at > start:
                end = split_at
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        start = max(end - chunk_overlap, start + 1)

    return chunks
