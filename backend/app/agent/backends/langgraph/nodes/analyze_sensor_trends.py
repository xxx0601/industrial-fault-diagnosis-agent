"""Analyze temperature and vibration trends across log timeline."""

from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.rules.timeline_rules import build_trend_summary
from app.agent.trace.mapper import NODE_ANALYZE_TRENDS
from app.models.log_entry import LogEntry


def analyze_sensor_trends_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    raw_entries = state.get("log_entries") or []
    entries = [LogEntry.from_dict(e) for e in raw_entries if isinstance(e, dict)]
    trend_summary = build_trend_summary(entries)

    temp_dir = trend_summary["temperature"]["direction"]
    vib_dir = trend_summary["vibration"]["direction"]
    message = f"温振趋势：温度 {temp_dir}，振动 {vib_dir}"

    return {
        "temperature_trend": trend_summary["temperature"],
        "vibration_trend": trend_summary["vibration"],
        "trend_summary": trend_summary,
        "trace": [
            make_trace_entry(
                NODE_ANALYZE_TRENDS,
                message,
                metadata={"trends": trend_summary},
            )
        ],
    }
