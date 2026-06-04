# Backend API

Industrial Fault Diagnosis Agent — FastAPI service.

## Quick start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8001
```

- Swagger: http://localhost:8001/docs
- Full docs: [../docs/README.md](../docs/README.md)

## Layout

| Package | Path |
|---------|------|
| Agent | `app/agent/` |
| RAG | `app/rag/` |
| Tools | `app/tools/` |
| API | `app/api/v1/` |
