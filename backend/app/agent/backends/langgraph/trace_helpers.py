"""Build trace dict entries inside LangGraph nodes."""

from typing import Any

from app.agent.trace.mapper import (
    NODE_ANALYZE_TRENDS,
    NODE_CREATE_WORK_ORDER,
    NODE_FAULT_TIMELINE,
    NODE_GENERATE_DIAGNOSIS,
    NODE_PARSE_TIMELINE,
    NODE_PARSE_SENSORS,
    NODE_RAG_RETRIEVE,
    NODE_READ_LOG,
    NODE_RISK_EVALUATION,
    NODE_TOOL_CALL,
)
from app.tools.base import ToolResult

NODE_LABELS: dict[str, str] = {
    NODE_READ_LOG: "Read Log",
    NODE_PARSE_TIMELINE: "Parse Timeline",
    NODE_PARSE_SENSORS: "Parse Sensor Data",
    NODE_ANALYZE_TRENDS: "Analyze Trends",
    NODE_FAULT_TIMELINE: "Fault Timeline",
    NODE_TOOL_CALL: "Tool Call",
    NODE_RAG_RETRIEVE: "RAG Retrieval",
    NODE_RISK_EVALUATION: "Risk Calculation",
    NODE_GENERATE_DIAGNOSIS: "Generate Diagnosis",
    NODE_CREATE_WORK_ORDER: "Create Work Order",
}

STEP_BY_NODE: dict[str, int] = {
    NODE_READ_LOG: 1,
    NODE_PARSE_TIMELINE: 2,
    NODE_ANALYZE_TRENDS: 3,
    NODE_TOOL_CALL: 4,
    NODE_FAULT_TIMELINE: 5,
    NODE_RAG_RETRIEVE: 6,
    NODE_RISK_EVALUATION: 7,
    NODE_GENERATE_DIAGNOSIS: 8,
    NODE_CREATE_WORK_ORDER: 9,
}

_tool_step_counter = 0


def make_trace_entry(
    node: str,
    message: str,
    *,
    status: str = "success",
    metadata: dict[str, Any] | None = None,
    step: int | None = None,
) -> dict[str, Any]:
    meta = {"node_label": NODE_LABELS.get(node, node)}
    if metadata:
        meta.update(metadata)
    return {
        "step": step if step is not None else STEP_BY_NODE.get(node, 0),
        "node": node,
        "message": message,
        "status": status,
        "metadata": meta,
    }


def make_tool_trace_entry(result: ToolResult, step: int) -> dict[str, Any]:
    return make_trace_entry(
        NODE_TOOL_CALL,
        f"Tool: {result.tool_name}",
        status=result.status,
        step=step,
        metadata={
            "node_label": "Tool Call",
            "tool_name": result.tool_name,
            "tool_input": result.input,
            "tool_output": result.output,
            "duration_ms": result.duration_ms,
            "error": result.error,
        },
    )
