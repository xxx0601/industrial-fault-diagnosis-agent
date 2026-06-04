"""Create work order when risk is HIGH."""

from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.context import get_tool_executor, get_tool_run_context
from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_tool_trace_entry, make_trace_entry
from app.agent.trace.mapper import NODE_CREATE_WORK_ORDER


def create_work_order_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    if state.get("risk_level") != "HIGH":
        return {
            "trace": [
                make_trace_entry(
                    NODE_CREATE_WORK_ORDER,
                    "风险未达 HIGH，跳过工单创建",
                    metadata={"skipped": True},
                )
            ],
        }

    executor = get_tool_executor(config)
    ctx = get_tool_run_context(state, config)
    fault_type = (
        (state.get("possible_causes") or ["unknown"])[0]
        if state.get("possible_causes")
        else state.get("fault_code") or "unknown"
    )
    result = executor.execute_one(
        "create_work_order",
        {
            "device_id": state.get("device_id") or state.get("file_id"),
            "fault_type": fault_type,
            "risk_level": state.get("risk_level") or "HIGH",
        },
        ctx,
    )
    work_order_id = result.output.get("work_order_id") if result.status == "success" else None
    return {
        "work_order_id": work_order_id,
        "tool_results": [result.to_dict()],
        "trace": [make_tool_trace_entry(result, step=7)],
    }


def should_create_work_order(state: DiagnosisState) -> str:
    if state.get("risk_level") == "HIGH":
        return "create_work_order"
    return "__end__"
