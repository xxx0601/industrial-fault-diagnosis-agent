"""Map agent runtime events to TraceStep — LangGraph stream + state trace."""

from typing import Any

from app.models.trace_step import TraceStep

NODE_READ_LOG = "read_log"
NODE_PARSE_SENSORS = "parse_sensor_data"
NODE_PARSE_TIMELINE = "parse_timeline"
NODE_ANALYZE_TRENDS = "analyze_sensor_trends"
NODE_FAULT_TIMELINE = "fault_timeline_analysis"
NODE_FAULT_ANALYSIS = "fault_analysis"
NODE_RISK_EVALUATION = "risk_evaluation"
NODE_TOOL_CALL = "tool_call"
NODE_RAG_RETRIEVE = "rag_retrieve"
NODE_GENERATE_DIAGNOSIS = "generate_diagnosis"
NODE_CREATE_WORK_ORDER = "create_work_order"

_PIPELINE_ORDER = [
    NODE_READ_LOG,
    NODE_PARSE_TIMELINE,
    NODE_PARSE_SENSORS,
    NODE_ANALYZE_TRENDS,
    NODE_FAULT_TIMELINE,
    NODE_TOOL_CALL,
    NODE_RAG_RETRIEVE,
    NODE_RISK_EVALUATION,
    NODE_GENERATE_DIAGNOSIS,
    NODE_CREATE_WORK_ORDER,
]

_NODE_LABELS: dict[str, str] = {
    NODE_READ_LOG: "Read Log",
    NODE_PARSE_TIMELINE: "Parse Timeline",
    NODE_PARSE_SENSORS: "Parse Sensor Data",
    NODE_ANALYZE_TRENDS: "Analyze Sensor Trends",
    NODE_FAULT_TIMELINE: "Fault Timeline Analysis",
    NODE_TOOL_CALL: "Tool Call",
    NODE_RAG_RETRIEVE: "RAG Retrieve",
    NODE_CREATE_WORK_ORDER: "Create Work Order",
    NODE_RISK_EVALUATION: "Risk Evaluation",
    NODE_GENERATE_DIAGNOSIS: "Generate Diagnosis",
}


def trace_entries_to_steps(entries: list[dict[str, Any]]) -> list[TraceStep]:
    """Convert trace dicts accumulated in DiagnosisState to TraceStep models."""
    sorted_entries = sorted(
        entries,
        key=lambda e: (
            e.get("step", 999),
            _PIPELINE_ORDER.index(e["node"])
            if e.get("node") in _PIPELINE_ORDER
            else 999,
        ),
    )
    steps: list[TraceStep] = []
    for idx, entry in enumerate(sorted_entries, start=1):
        node = entry.get("node", f"step_{idx}")
        metadata = dict(entry.get("metadata") or {})
        metadata.setdefault("node_label", _NODE_LABELS.get(node, node))
        steps.append(
            TraceStep(
                step=int(entry.get("step") or idx),
                node=node,
                message=entry.get("message", ""),
                status=entry.get("status", "success"),
                metadata=metadata,
            )
        )
    return steps


def map_langgraph_stream_updates(updates: list[dict[str, Any]]) -> list[TraceStep]:
    """Build TraceStep list from LangGraph stream_mode='updates' chunks."""
    entries: list[dict[str, Any]] = []
    for chunk in updates:
        if not isinstance(chunk, dict):
            continue
        for _node_name, node_output in chunk.items():
            if not isinstance(node_output, dict):
                continue
            trace_part = node_output.get("trace") or []
            if isinstance(trace_part, list):
                entries.extend(trace_part)
    return trace_entries_to_steps(entries)


def map_langgraph_execution_history(events: list[dict[str, Any]]) -> list[TraceStep]:
    """Alias for stream updates — used when persisting raw execution history."""
    return map_langgraph_stream_updates(events)


def legacy_strings_to_steps(messages: list[str]) -> list[TraceStep]:
    """Upgrade v1 string traces stored in diagnosis_index.json."""
    defaults = list(_NODE_LABELS.items())
    steps: list[TraceStep] = []
    for idx, message in enumerate(messages, start=1):
        node_id, node_label = (
            defaults[idx - 1] if idx <= len(defaults) else (f"step_{idx}", f"Step {idx}")
        )
        steps.append(
            TraceStep(
                step=idx,
                node=node_id,
                message=message,
                status="success",
                metadata={"node_label": node_label},
            )
        )
    return steps


def serialize_state_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    """Persist a JSON-safe subset of DiagnosisState in execution_meta."""
    keys = (
        "file_id",
        "request_fault_code",
        "log_content",
        "log_entries",
        "fault_codes",
        "parsed_data",
        "fault_code",
        "primary_fault",
        "related_faults",
        "fault_evolution",
        "trend_summary",
        "temperature_trend",
        "vibration_trend",
        "risk_level",
        "possible_causes",
        "recommendations",
        "rag_chunks",
        "tool_results",
        "risk_score",
        "work_order_id",
        "tool_plan",
    )
    snapshot = {k: state[k] for k in keys if k in state}
    if "log_content" in snapshot and isinstance(snapshot["log_content"], str):
        content = snapshot["log_content"]
        if len(content) > 2000:
            snapshot["log_content"] = content[:2000] + "…"
    return snapshot
