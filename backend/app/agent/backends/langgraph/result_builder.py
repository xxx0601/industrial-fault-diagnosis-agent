"""Build DiagnosisResult from LangGraph final state."""

from typing import Any

from app.models.diagnosis_result import DiagnosisResult, FaultRef, TrendMetric


def _fault_ref(data: dict[str, Any] | None) -> FaultRef | None:
    if not data or not data.get("code"):
        return None
    return FaultRef(
        code=str(data["code"]),
        description=str(data.get("description", "")),
    )


def _fault_refs(items: list[dict[str, Any]] | None) -> list[FaultRef]:
    refs: list[FaultRef] = []
    for item in items or []:
        ref = _fault_ref(item)
        if ref:
            refs.append(ref)
    return refs


def _trend_metric(data: dict[str, Any] | None) -> TrendMetric | None:
    if not data:
        return None
    return TrendMetric.from_dict(data)


def build_diagnosis_result(merged: dict[str, Any]) -> DiagnosisResult:
    return DiagnosisResult(
        risk_level=merged.get("risk_level") or "LOW",
        possible_causes=list(merged.get("possible_causes") or []),
        recommendations=list(merged.get("recommendations") or []),
        fault_codes=list(merged.get("fault_codes") or []),
        primary_fault=_fault_ref(merged.get("primary_fault")),
        related_faults=_fault_refs(merged.get("related_faults")),
        fault_evolution=list(merged.get("fault_evolution") or []),
        temperature_trend=_trend_metric(merged.get("temperature_trend")),
        vibration_trend=_trend_metric(merged.get("vibration_trend")),
    )
