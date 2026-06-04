from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.rules.diagnosis_rules import assess_risk_level, params_from_parsed
from app.agent.trace.mapper import NODE_RISK_EVALUATION


def risk_evaluation_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    parsed_data = state.get("parsed_data") or {}
    params = params_from_parsed(parsed_data)
    risk_score = int(state.get("risk_score") or 0)

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = assess_risk_level(params)

    trends = state.get("trend_summary") or {}
    temp_dir = (trends.get("temperature") or {}).get("direction")
    vib_dir = (trends.get("vibration") or {}).get("direction")
    if temp_dir == "rising" or vib_dir == "rising":
        order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        if order.get(risk_level, 0) < 1:
            risk_level = "MEDIUM"
        if temp_dir == "rising" and vib_dir == "rising" and order.get(risk_level, 0) < 2:
            risk_level = "HIGH"

    return {
        "risk_level": risk_level,
        "trace": [
            make_trace_entry(
                NODE_RISK_EVALUATION,
                f"评估风险等级 {risk_level}（risk_score={risk_score}）",
                metadata={"risk_level": risk_level, "risk_score": risk_score},
            )
        ],
    }
