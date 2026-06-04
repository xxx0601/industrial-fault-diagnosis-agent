"""Plan which tools to invoke based on parsed diagnosis context."""

from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
def tool_router_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    parsed = state.get("parsed_data") or {}
    device_id = state.get("device_id") or state.get("file_id", "unknown")
    codes = list(state.get("fault_codes") or [])
    if not codes and state.get("fault_code"):
        codes = [state["fault_code"]]

    plan: list[dict] = []

    for code in codes:
        plan.append(
            {
                "tool": "query_fault_code",
                "input": {"fault_code": code},
            }
        )

    plan.append(
        {
            "tool": "query_device_status",
            "input": {"device_id": device_id},
        }
    )

    plan.append(
        {
            "tool": "calculate_risk_score",
            "input": {
                "temperature": float(parsed.get("temperature", 72)),
                "pressure": float(parsed.get("pressure", 20)),
                "rpm": float(parsed.get("rpm", 3000)),
                "vibration": float(parsed.get("vibration", 3.5)),
            },
        }
    )

    return {
        "device_id": device_id,
        "tool_plan": plan,
    }
