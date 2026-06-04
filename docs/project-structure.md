# Project Structure

```
industrial-fault-diagnosis-agent/
├── .github/workflows/          # CI (optional)
├── docs/                       # Documentation
│   ├── images/                 # Screenshots
│   └── *.md
├── scripts/
│   └── test_diagnosis_flow.py
├── frontend/                   # Next.js 15
│   └── src/
│       ├── app/                # Pages
│       ├── components/
│       └── features/           # API clients
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/
│   │   ├── core/
│   │   ├── agent/              # ★ Agent (unified)
│   │   │   ├── backends/
│   │   │   │   ├── langgraph/
│   │   │   │   │   └── nodes/
│   │   │   │   ├── langgraph_agent.py
│   │   │   │   └── mock_agent.py
│   │   │   ├── workflows/
│   │   │   ├── rules/
│   │   │   └── trace/
│   │   ├── rag/                # ★ RAG
│   │   ├── tools/              # ★ Tools
│   │   ├── parsers/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── storage/
│   │   └── services/
│   ├── data/
│   │   └── samples/            # Committed test logs
│   ├── tests/
│   ├── uploads/                # Runtime (gitignored)
│   └── requirements.txt
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── requirements.txt            # → backend/requirements.txt
```
