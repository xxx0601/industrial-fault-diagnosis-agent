# Contributing

Thank you for contributing to **Industrial Fault Diagnosis Agent**.

## Development setup

1. Fork and clone the repository.
2. Backend: `cd backend && python -m venv .venv && pip install -r requirements-dev.txt`
3. Frontend: `cd frontend && npm install`
4. Copy `backend/.env.example` → `backend/.env` and `frontend/.env.local.example` → `frontend/.env.local`

## Running locally

```bash
# Terminal 1
cd backend && uvicorn app.main:app --reload --port 8001

# Terminal 2
cd frontend && npm run dev
```

## Tests

```bash
cd backend
python -m pytest tests/ -q

# E2E (API must be running)
python ../scripts/test_diagnosis_flow.py
```

## Pull requests

- Keep changes focused; one feature or fix per PR.
- Update `docs/` when changing Agent graph, API, or environment variables.
- Ensure pytest passes before requesting review.

## Code layout (Scheme A)

- `frontend/` — Next.js UI
- `backend/app/agent/` — LangGraph, mock, rules, trace
- `backend/app/rag/` — knowledge retrieval
- `backend/app/tools/` — tool implementations
- `docs/` — architecture and API documentation
