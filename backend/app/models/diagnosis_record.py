"""Domain record for a completed diagnosis session."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.models.diagnosis_result import DiagnosisResult
from app.models.trace_step import TraceStep


@dataclass(frozen=True)
class DiagnosisRecord:
    diagnosis_id: str
    file_id: str
    fault_code: str | None
    diagnosis_result: DiagnosisResult
    trace: list[TraceStep]
    created_at: datetime
    execution_meta: dict[str, Any] = field(default_factory=dict)
