"""Compile Industrial Fault Diagnosis Agent as a LangGraph StateGraph (v4 timeline)."""

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agent.backends.langgraph.nodes import (
    analyze_sensor_trends_node,
    create_work_order_node,
    fault_timeline_analysis_node,
    generate_diagnosis_node,
    parse_timeline_node,
    rag_retrieve_node,
    read_log_node,
    risk_evaluation_node,
    should_create_work_order,
    tool_executor_node,
    tool_router_node,
)
from app.agent.backends.langgraph.state import DiagnosisState

GRAPH_ID = "industrial_fault_diagnosis_v4_timeline"


def build_diagnosis_graph():
    workflow = StateGraph(DiagnosisState)

    workflow.add_node("read_log", read_log_node)
    workflow.add_node("parse_timeline", parse_timeline_node)
    workflow.add_node("analyze_sensor_trends", analyze_sensor_trends_node)
    workflow.add_node("tool_router", tool_router_node)
    workflow.add_node("tool_executor", tool_executor_node)
    workflow.add_node("fault_timeline_analysis", fault_timeline_analysis_node)
    workflow.add_node("rag_retrieve", rag_retrieve_node)
    workflow.add_node("risk_evaluation", risk_evaluation_node)
    workflow.add_node("generate_diagnosis", generate_diagnosis_node)
    workflow.add_node("create_work_order", create_work_order_node)

    workflow.add_edge(START, "read_log")
    workflow.add_edge("read_log", "parse_timeline")
    workflow.add_edge("parse_timeline", "analyze_sensor_trends")
    workflow.add_edge("analyze_sensor_trends", "tool_router")
    workflow.add_edge("tool_router", "tool_executor")
    workflow.add_edge("tool_executor", "fault_timeline_analysis")
    workflow.add_edge("fault_timeline_analysis", "rag_retrieve")
    workflow.add_edge("rag_retrieve", "risk_evaluation")
    workflow.add_edge("risk_evaluation", "generate_diagnosis")
    workflow.add_conditional_edges(
        "generate_diagnosis",
        should_create_work_order,
        {"create_work_order": "create_work_order", "__end__": END},
    )
    workflow.add_edge("create_work_order", END)

    return workflow.compile()


@lru_cache
def get_compiled_graph():
    return build_diagnosis_graph()
