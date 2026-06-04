"""Diagnosis agent contracts — LangGraph and Mock implementations."""

from dataclasses import dataclass
from typing import Protocol

from app.models.device_params import DeviceParams
from app.models.diagnosis_result import DiagnosisResult
from app.models.trace_step import TraceStep
from app.services.upload_service import UploadService


@dataclass(frozen=True)
class DiagnosisContext:
    """Legacy context — prefer AgentRunResult via agent.run()."""

    file_id: str
    log_text: str
    params: DeviceParams
    fault_code: str | None


@dataclass(frozen=True)
class AgentDiagnosisResult:
    risk_level: str
    possible_causes: list[str]
    recommendations: list[str]


@dataclass(frozen=True)
class AgentRunResult:
    """Unified output from Mock or LangGraph agent runs."""

    diagnosis_result: DiagnosisResult
    trace: list[TraceStep]
    fault_code: str | None
    execution_meta: dict


class DiagnosisAgentProtocol(Protocol):
    def run(
        self,
        file_id: str,
        fault_code: str | None,
        upload_service: UploadService,
    ) -> AgentRunResult:
        """Execute full diagnosis workflow."""

    def diagnose(self, ctx: DiagnosisContext) -> AgentDiagnosisResult:
        """Legacy entry — optional for backward compatibility."""
