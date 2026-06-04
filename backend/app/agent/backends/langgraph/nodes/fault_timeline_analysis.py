"""Infer primary fault, related faults, and evolution chain from timeline."""

from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.rules.timeline_rules import (
    build_fault_evolution,
    merge_fault_descriptions,
    select_primary_fault,
    select_related_faults,
)
from app.agent.trace.mapper import NODE_FAULT_TIMELINE
from app.models.log_entry import LogEntry


def fault_timeline_analysis_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    raw_entries = state.get("log_entries") or []
    entries = [LogEntry.from_dict(e) for e in raw_entries if isinstance(e, dict)]
    fault_codes = list(state.get("fault_codes") or [])
    trend_summary = state.get("trend_summary") or {}

    lookup = merge_fault_descriptions(state.get("tool_results"))
    lookup = {**lookup, **(state.get("fault_code_lookup") or {})}
    primary = select_primary_fault(
        fault_codes,
        entries,
        state.get("request_fault_code"),
    )
    related = select_related_faults(fault_codes, primary, lookup)
    evolution = build_fault_evolution(fault_codes, trend_summary, "LOW")

    fault_code = (primary or {}).get("code") or state.get("fault_code")
    causes: list[str] = []
    if primary:
        causes.append(f"{primary['code']} {primary['description']}")
    for item in related:
        causes.append(f"{item['code']} {item['description']}")

    message = (
        f"主要故障 {primary['code']} {primary['description']}"
        if primary
        else "未确定主要故障"
    )

    return {
        "primary_fault": primary,
        "related_faults": related,
        "fault_evolution": evolution,
        "fault_code": fault_code,
        "possible_causes": causes,
        "trace": [
            make_trace_entry(
                NODE_FAULT_TIMELINE,
                message,
                metadata={
                    "primary_fault": primary,
                    "related_faults": related,
                    "fault_evolution": evolution,
                    "fault_codes": fault_codes,
                },
            )
        ],
    }
