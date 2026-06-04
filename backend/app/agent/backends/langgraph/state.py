"""LangGraph shared state for Industrial Fault Diagnosis Agent."""

import operator
from typing import Annotated, Any, TypedDict


def _last_value(_left: Any, right: Any) -> Any:
    """Reducer for scalar fields — last node write wins."""
    return right


class DiagnosisState(TypedDict, total=False):
    # --- inputs ---
    file_id: str
    request_fault_code: str | None
    device_id: Annotated[str, _last_value]

    # --- pipeline ---
    log_content: Annotated[str, _last_value]
    log_entries: Annotated[list[dict[str, Any]], _last_value]
    fault_codes: Annotated[list[str], _last_value]
    parsed_data: Annotated[dict[str, Any], _last_value]
    fault_code: Annotated[str | None, _last_value]
    temperature_trend: Annotated[dict[str, Any], _last_value]
    vibration_trend: Annotated[dict[str, Any], _last_value]
    trend_summary: Annotated[dict[str, Any], _last_value]
    primary_fault: Annotated[dict[str, str] | None, _last_value]
    related_faults: Annotated[list[dict[str, str]], _last_value]
    fault_evolution: Annotated[list[str], _last_value]
    fault_code_lookup: Annotated[dict[str, str], _last_value]
    tool_plan: Annotated[list[dict[str, Any]], _last_value]
    risk_score: Annotated[int, _last_value]
    possible_causes: Annotated[list[str], _last_value]
    risk_level: Annotated[str, _last_value]
    recommendations: Annotated[list[str], _last_value]
    work_order_id: Annotated[str | None, _last_value]

    # --- observability (append per node) ---
    trace: Annotated[list[dict[str, Any]], operator.add]

    # --- reserved for Step 6+ ---
    rag_chunks: Annotated[list[dict[str, Any]], operator.add]
    tool_results: Annotated[list[dict[str, Any]], operator.add]
    agent_messages: Annotated[list[dict[str, Any]], operator.add]
    errors: Annotated[list[str], operator.add]
