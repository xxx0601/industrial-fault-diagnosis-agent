"""LangGraph-backed diagnosis agent — Industrial Fault Diagnosis Agent."""

from typing import Any

from app.agent.base import AgentRunResult
from app.core.config import get_settings
from app.agent.backends.langgraph.context import build_run_config
from app.agent.backends.langgraph.graph import GRAPH_ID, get_compiled_graph
from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.trace.mapper import (
    map_langgraph_stream_updates,
    serialize_state_snapshot,
    trace_entries_to_steps,
)
from app.agent.backends.langgraph.result_builder import build_diagnosis_result
from app.repositories.work_order_repo import WorkOrderRepository
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.upload_service import UploadService
from app.tools.executor import ToolExecutor
from app.tools.registry import build_default_registry
from pathlib import Path


class LangGraphDiagnosisAgent:
    def __init__(self, knowledge_service: KnowledgeBaseService | None = None) -> None:
        self._knowledge = knowledge_service

    def run(
        self,
        file_id: str,
        fault_code: str | None,
        upload_service: UploadService,
    ) -> AgentRunResult:
        graph = get_compiled_graph()
        initial: DiagnosisState = {
            "file_id": file_id,
            "request_fault_code": fault_code,
            "trace": [],
            "rag_chunks": [],
            "tool_results": [],
            "agent_messages": [],
            "errors": [],
        }
        settings = get_settings()
        knowledge = self._knowledge
        if knowledge is None:
            from app.services.knowledge_base_service import build_knowledge_base_service

            knowledge = build_knowledge_base_service(settings)
        registry = build_default_registry()
        executor = ToolExecutor(registry)
        work_order_repo = WorkOrderRepository(
            Path(settings.work_order_index_path).resolve()
        )
        work_order_repo.ensure_ready()
        config = build_run_config(
            upload_service,
            knowledge,
            settings,
            executor,
            work_order_repo,
        )

        merged: dict[str, Any] = dict(initial)
        stream_updates: list[dict[str, Any]] = []
        for chunk in graph.stream(initial, stream_mode="updates", config=config):
            stream_updates.append(chunk)
            for _node, node_out in chunk.items():
                if isinstance(node_out, dict):
                    for key, value in node_out.items():
                        if key == "trace" and isinstance(value, list):
                            merged.setdefault("trace", [])
                            merged["trace"] = [*merged.get("trace", []), *value]
                        else:
                            merged[key] = value

        trace = trace_entries_to_steps(merged.get("trace") or [])
        if not trace:
            trace = map_langgraph_stream_updates(stream_updates)

        result = build_diagnosis_result(merged)

        return AgentRunResult(
            fault_code=merged.get("fault_code"),
            diagnosis_result=result,
            trace=trace,
            execution_meta={
                "agent_backend": "langgraph",
                "graph_id": GRAPH_ID,
                "final_state": serialize_state_snapshot(merged),
                "langgraph_updates": stream_updates,
            },
        )
