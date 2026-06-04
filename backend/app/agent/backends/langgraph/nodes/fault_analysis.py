from langchain_core.runnables import RunnableConfig

from app.agent.backends.langgraph.state import DiagnosisState
from app.agent.backends.langgraph.trace_helpers import make_trace_entry
from app.agent.rules.diagnosis_rules import resolve_causes_from_fault_code
from app.agent.trace.mapper import NODE_FAULT_ANALYSIS


def fault_analysis_node(state: DiagnosisState, config: RunnableConfig) -> dict:
    _ = config
    fault_code = state.get("fault_code")
    causes = resolve_causes_from_fault_code(fault_code)
    message = f"识别故障码 {fault_code}" if fault_code else "未识别到故障码"
    return {
        "possible_causes": causes,
        "trace": [
            make_trace_entry(
                NODE_FAULT_ANALYSIS,
                message,
                metadata={"fault_code": fault_code, "possible_causes": causes},
            )
        ],
    }
