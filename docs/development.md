# Development Guide

## Quick start

```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8001

# Frontend
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

## E2E script

From repository root (API running):

```powershell
.\backend\.venv\Scripts\python.exe scripts\test_diagnosis_flow.py
```

Default log: `backend/data/samples/timeline_fault_chain.json`

## Pytest

```powershell
cd backend
python -m pytest tests/ -q
```

## Agent backend switch

Set `AGENT_BACKEND=mock` in `backend/.env` to use rule-based mock without LangGraph tools/RAG nodes in graph (timeline logic still shared via `app/agent/workflows/timeline.py`).
