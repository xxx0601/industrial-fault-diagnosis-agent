from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.rules.diagnosis_rules import (
    build_recommendations,
    merge_rag_recommendations,
    params_from_parsed,
    resolve_possible_causes,
)
from app.agent.rules.timeline_rules import build_fault_evolution
from app.agent.trace.mapper import NODE_GENERATE_DIAGNOSIS


def generate_diagnosis_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    parsed_data = state.get("parsed_data") or {}
    params = params_from_parsed(parsed_data)
    fault_code = state.get("fault_code")
    risk_level = state.get("risk_level") or "LOW"
    causes = list(state.get("possible_causes") or [])
    if not causes:
        causes = resolve_possible_causes(fault_code, params, risk_level)
    fault_codes = state.get("fault_codes") or []
    trend_summary = state.get("trend_summary") or {}
    evolution = list(state.get("fault_evolution") or [])
    if not evolution and fault_codes:
        evolution = build_fault_evolution(fault_codes, trend_summary, risk_level)
    elif risk_level == "HIGH" and "设备进入高风险状态" not in evolution:
        evolution = [*evolution, "设备进入高风险状态"]
    recommendations = build_recommendations(causes, params, risk_level)
    rag_chunks = state.get("rag_chunks") or []
    if rag_chunks:
        recommendations = merge_rag_recommendations(recommendations, rag_chunks)
    return {
        "possible_causes": causes,
        "recommendations": recommendations,
        "fault_evolution": evolution,
        "trace": [
            make_trace_entry(
                NODE_GENERATE_DIAGNOSIS,
                "生成维修建议",
                metadata={
                    "possible_causes": causes,
                    "recommendations": recommendations,
                    "primary_fault": state.get("primary_fault"),
                    "related_faults": state.get("related_faults"),
                    "fault_evolution": evolution,
                    "fault_codes": fault_codes,
                    "trends": trend_summary,
                    "rag_enhanced": bool(rag_chunks),
                },
            )
        ],
    }
