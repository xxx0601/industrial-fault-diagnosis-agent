"""Execute tool plan via ToolExecutor — sequential with dynamic inputs."""

from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.context import get_tool_executor, get_tool_run_context
from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_tool_trace_entry


def tool_executor_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    executor = get_tool_executor(config)
    ctx = get_tool_run_context(state, config)
    plan = list(state.get("tool_plan") or [])

    results = []
    trace_entries = []
    parsed_update: dict = {}
    risk_score = 0
    device_telemetry: dict = {}

    base_step = 3
    for idx, step in enumerate(plan):
        tool_name = step.get("tool") or step.get("name")
        payload = dict(step.get("input") or {})

        if tool_name == "calculate_risk_score" and device_telemetry:
            payload = {
                "temperature": device_telemetry.get("temperature", payload.get("temperature", 72)),
                "pressure": device_telemetry.get("pressure", payload.get("pressure", 20)),
                "rpm": device_telemetry.get("rpm", payload.get("rpm", 3000)),
                "vibration": device_telemetry.get("vibration", payload.get("vibration", 3.5)),
            }

        result = executor.execute_one(tool_name, payload, ctx)
        results.append(result)
        trace_entries.append(make_tool_trace_entry(result, step=base_step + idx))

        if result.status != "success":
            continue
        if result.tool_name == "query_device_status":
            device_telemetry = result.output
            parsed_update = result.output
        elif result.tool_name == "calculate_risk_score":
            risk_score = int(result.output.get("risk_score", 0))

    fault_code_lookup: dict[str, str] = {}
    possible_causes: list[str] = []
    for result in results:
        if result.status != "success" or result.tool_name != "query_fault_code":
            continue
        out = result.output or {}
        code = str(out.get("fault_code", "")).upper()
        desc = out.get("description")
        if code and desc:
            fault_code_lookup[code] = str(desc)
            label = f"{code} {desc}"
            if label not in possible_causes:
                possible_causes.append(label)

    merged_parsed = {**(state.get("parsed_data") or {}), **parsed_update}

    return {
        "parsed_data": merged_parsed,
        "possible_causes": possible_causes or state.get("possible_causes") or [],
        "fault_code_lookup": fault_code_lookup,
        "risk_score": risk_score,
        "tool_results": [r.to_dict() for r in results],
        "trace": trace_entries,
    }
