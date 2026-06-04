"""Agent factory — mock | langgraph."""

from functools import lru_cache

from app.agent.base import DiagnosisAgentProtocol
from app.agent.backends.langgraph_agent import LangGraphDiagnosisAgent
from app.agent.backends.mock_agent import MockDiagnosisAgent
from app.core.config import get_settings
from app.services.knowledge_base_service import build_knowledge_base_service


@lru_cache
def get_diagnosis_agent() -> DiagnosisAgentProtocol:
    settings = get_settings()
    backend = settings.agent_backend.lower()
    if backend == "langgraph":
        return LangGraphDiagnosisAgent(
            knowledge_service=build_knowledge_base_service(settings)
        )
    return MockDiagnosisAgent()
