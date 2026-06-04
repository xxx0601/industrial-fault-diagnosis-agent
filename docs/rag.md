# RAG Pipeline

1. **Upload** — `POST /api/v1/knowledge/upload` (PDF/TXT)
2. **Parse** — `app/rag/parsers/`
3. **Chunk** — `app/rag/chunking.py`
4. **Index** — ChromaDB or `memory_store` (`VECTOR_STORE_BACKEND=auto`)
5. **Retrieve** — `rag_retrieve` node builds query from fault codes & evolution
6. **Enhance** — `merge_rag_recommendations` in diagnosis generation

## Configuration

| Variable | Default |
|----------|---------|
| `RAG_ENABLED` | `true` |
| `VECTOR_STORE_BACKEND` | `auto` |
| `RAG_DEFAULT_TOP_K` | `5` |
| `RAG_CHUNK_SIZE` | `800` |

See [configuration.md](configuration.md).
