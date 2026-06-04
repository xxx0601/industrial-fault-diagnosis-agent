"""Parse full log into timeline entries and fault code list."""

from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.rules.diagnosis_rules import resolve_fault_code
from app.agent.trace.mapper import NODE_PARSE_TIMELINE
from app.parsers.log_parser import LogParser
from app.parsers.timeline_parser import (
    TimelineParser,
    collect_fault_codes,
    snapshot_from_entries,
)


def parse_timeline_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    log_content = state.get("log_content") or ""
    timeline_parser = TimelineParser()
    entries = timeline_parser.parse(log_content)
    log_entries = [e.to_dict() for e in entries]

    fault_codes = collect_fault_codes(entries)
    snapshot = snapshot_from_entries(entries)

    # Legacy flat parse fills gaps when timeline has no per-entry sensors
    if not snapshot.get("temperature") and not snapshot.get("vibration"):
        legacy = LogParser().parse(log_content)
        for field in ("temperature", "pressure", "rpm", "vibration", "fault_code"):
            val = getattr(legacy, field, None)
            if val is not None and field not in snapshot:
                snapshot[field] = val
        if not fault_codes and legacy.fault_code:
            fault_codes = [legacy.fault_code]
            snapshot["fault_code"] = legacy.fault_code

    parsed_data = {k: v for k, v in snapshot.items() if v is not None}
    primary_candidate = fault_codes[-1] if fault_codes else parsed_data.get("fault_code")
    fault_code = resolve_fault_code(
        state.get("request_fault_code"),
        str(primary_candidate) if primary_candidate else None,
    )
    if fault_code:
        parsed_data["fault_code"] = fault_code

    device_id = parsed_data.get("device_id") or state.get("file_id", "unknown")
    message = (
        f"解析时间线 {len(log_entries)} 条，识别故障码 {', '.join(fault_codes)}"
        if fault_codes
        else f"解析时间线 {len(log_entries)} 条，未发现故障码"
    )

    return {
        "log_entries": log_entries,
        "fault_codes": fault_codes,
        "parsed_data": parsed_data,
        "fault_code": fault_code,
        "device_id": str(device_id),
        "trace": [
            make_trace_entry(
                NODE_PARSE_TIMELINE,
                message,
                metadata={
                    "entry_count": len(log_entries),
                    "fault_codes": fault_codes,
                    "parsed_data": parsed_data,
                },
            )
        ],
    }
