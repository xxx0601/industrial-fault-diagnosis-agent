# Configuration

Copy `backend/.env.example` to `backend/.env`.

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PORT` | `8001` | API port |
| `CORS_ORIGINS` | `http://localhost:3001,...` | Allowed origins |
| `AGENT_BACKEND` | `langgraph` | `langgraph` or `mock` |
| `RAG_ENABLED` | `true` | Enable RAG node |
| `VECTOR_STORE_BACKEND` | `auto` | `auto`, `chroma`, `memory` |
| `UPLOAD_DIR` | `uploads` | Device log storage |
| `DIAGNOSIS_INDEX_PATH` | `data/diagnosis_index.json` | Diagnosis index |
| `WORK_ORDER_INDEX_PATH` | `data/work_orders_index.json` | Work orders |

Frontend: `NEXT_PUBLIC_API_URL` in `frontend/.env.local`.
