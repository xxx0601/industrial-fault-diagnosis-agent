"""RAG retrieval node — query knowledge base for maintenance context."""

from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.context import get_knowledge_service, get_settings_from_config
from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.trace.mapper import NODE_RAG_RETRIEVE


def _build_rag_query(state: DiagnosisState) -> str:
    parts: list[str] = []
    for code in state.get("fault_codes") or []:
        parts.append(f"故障码 {code} 维修")
    primary = state.get("primary_fault") or {}
    if primary.get("description"):
        parts.append(str(primary["description"]))
    evolution = state.get("fault_evolution") or []
    for step in evolution[:3]:
        parts.append(step)
    fault_code = state.get("fault_code")
    if fault_code and f"故障码 {fault_code}" not in " ".join(parts):
        parts.append(f"故障码 {fault_code} 维修")
    parsed = state.get("parsed_data") or {}
    if parsed.get("temperature") is not None:
        parts.append(f"温度 {parsed['temperature']} 冷却")
    if parsed.get("vibration") is not None:
        parts.append(f"振动 {parsed['vibration']} 轴承")
    causes = state.get("possible_causes") or []
    for cause in causes[:2]:
        parts.append(cause)
    if not parts:
        parts.append("工业设备 故障诊断 维修手册")
    return " ".join(parts)


def rag_retrieve_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    settings = get_settings_from_config(config)
    if not settings.rag_enabled:
        return {
            "rag_chunks": [],
            "trace": [
                make_trace_entry(
                    NODE_RAG_RETRIEVE,
                    "RAG 已禁用，跳过知识库检索",
                    metadata={"hits": [], "query": ""},
                )
            ],
        }

    knowledge = get_knowledge_service(config)
    query = _build_rag_query(state)
    response = knowledge.search(query, settings.rag_default_top_k)
    chunks = [
        {
            "doc_id": h.doc_id,
            "doc_name": h.doc_name,
            "chunk_text": h.chunk_text,
            "similarity_score": h.similarity_score,
            "chunk_index": h.chunk_index,
        }
        for h in response.hits
    ]

    if chunks:
        doc_names = list({c.get("doc_name") or c["doc_id"] for c in chunks})
        message = f"检索到 {len(chunks)} 条相关知识（{', '.join(doc_names[:3])}）"
    else:
        message = "知识库暂无匹配内容"

    return {
        "rag_chunks": chunks,
        "trace": [
            make_trace_entry(
                NODE_RAG_RETRIEVE,
                message,
                metadata={
                    "query": query,
                    "hits": chunks,
                    "matched_documents": list(
                        {c.get("doc_name") or c["doc_id"] for c in chunks}
                    ),
                },
            )
        ],
    }
