# API Reference

**Base URL:** `http://localhost:8001/api/v1`  
**OpenAPI:** `http://localhost:8001/docs`

## Health

| Method | Path |
|--------|------|
| GET | `/health` |

## Uploads

| Method | Path | Description |
|--------|------|-------------|
| POST | `/uploads` | Upload device log (multipart `file`) |
| GET | `/uploads` | List uploads |

## Diagnosis

| Method | Path | Description |
|--------|------|-------------|
| POST | `/diagnosis` | Run agent (`file_id`, optional `fault_code`) |
| GET | `/diagnosis/{id}` | Detail, trace, RAG sources, log entries |

## Knowledge

| Method | Path | Description |
|--------|------|-------------|
| POST | `/knowledge/upload` | Upload PDF/TXT |
| GET | `/knowledge/documents` | List documents |
| DELETE | `/knowledge/documents/{doc_id}` | Delete document |
| GET | `/knowledge/search` | Debug search |
