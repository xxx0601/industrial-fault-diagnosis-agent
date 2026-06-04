"""Industrial Fault Diagnosis Agent — orchestration, rules, LangGraph backends."""

from app.agent.registry import get_diagnosis_agent

__all__ = ["get_diagnosis_agent"]
