# Architecture

## Layered view

```mermaid
flowchart TB
  subgraph Frontend["Frontend · Next.js"]
    UI["Upload / Diagnose / Detail / Knowledge"]
  end

  subgraph FastAPI["FastAPI"]
    API["/api/v1/*"]
  end

  subgraph LangGraph["LangGraph Agent v4"]
    LG["StateGraph nodes"]
  end

  subgraph ToolCalling["Tool Calling"]
    TC["tool_router → tool_executor"]
  end

  subgraph RAGRetriever["RAG Retriever"]
    RR["rag_retrieve node"]
  end

  subgraph KnowledgeBase["Knowledge Base"]
    KB["PDF/TXT · Vector store"]
  end

  subgraph RiskEvaluation["Risk Evaluation"]
    RE["rules + calculate_risk_score + trends"]
  end

  subgraph WorkOrderService["Work Order Service"]
    WO["create_work_order · HIGH risk"]
  end

  subgraph TraceService["Trace Service"]
    TR["trace mapper · execution_meta"]
  end

  UI --> API
  API --> LG
  LG --> TC
  TC --> LG
  LG --> RR
  RR --> KB
  KB --> RR
  RR --> LG
  LG --> RE
  RE --> LG
  LG --> WO
  LG -.-> TR
  API -.-> TR
  UI -.-> TR
```

## Backend packages

| Path | Role |
|------|------|
| `backend/app/api/` | REST routes |
| `backend/app/agent/` | Agent orchestration (LangGraph, mock, rules, trace) |
| `backend/app/rag/` | Ingest, chunking, vector search |
| `backend/app/tools/` | Tool registry & implementations |
| `backend/app/services/` | Application services (diagnosis, upload, knowledge) |
| `backend/app/parsers/` | Log & timeline parsing |
