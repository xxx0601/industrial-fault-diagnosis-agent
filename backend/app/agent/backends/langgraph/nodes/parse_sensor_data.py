from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.rules.diagnosis_rules import resolve_fault_code
from app.agent.trace.mapper import NODE_PARSE_SENSORS
from app.parsers.log_parser import LogParser


def parse_sensor_data_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    parser = LogParser()
    params = parser.parse(state.get("log_content") or "")
    parsed_data = {
        k: v
        for k, v in {
            "temperature": params.temperature,
            "pressure": params.pressure,
            "rpm": params.rpm,
            "vibration": params.vibration,
            "fault_code": params.fault_code,
        }.items()
        if v is not None
    }
    fault_code = resolve_fault_code(
        state.get("request_fault_code"),
        parsed_data.get("fault_code"),
    )
    if fault_code:
        parsed_data["fault_code"] = fault_code

    device_id = parsed_data.get("device_id") or state.get("file_id", "unknown")

    return {
        "parsed_data": parsed_data,
        "fault_code": fault_code,
        "device_id": str(device_id),
        "trace": [
            make_trace_entry(
                NODE_PARSE_SENSORS,
                "解析设备参数",
                metadata={"params": parsed_data},
            )
        ],
    }
