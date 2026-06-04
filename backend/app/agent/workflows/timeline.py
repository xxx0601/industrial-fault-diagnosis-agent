"""Shared timeline diagnosis logic — used by Mock agent and tests."""

from dataclasses import dataclass
from typing import Any

from app.agent.rules.diagnosis_rules import (
    assess_risk_level,
    build_recommendations,
    params_from_parsed,
    resolve_fault_code,
    resolve_possible_causes,
)
from app.agent.rules.timeline_rules import (
    build_fault_evolution,
    build_trend_summary,
    select_primary_fault,
    select_related_faults,
)
from app.models.diagnosis_result import DiagnosisResult, FaultRef, TrendMetric
from app.models.log_entry import LogEntry
from app.parsers.log_parser import LogParser
from app.parsers.timeline_parser import (
    TimelineParser,
    collect_fault_codes,
    snapshot_from_entries,
)


@dataclass
class TimelineDiagnosisOutput:
    fault_code: str | None
    fault_codes: list[str]
    log_entries: list[dict[str, Any]]
    parsed_data: dict[str, Any]
    primary_fault: dict[str, str] | None
    related_faults: list[dict[str, str]]
    fault_evolution: list[str]
    temperature_trend: dict[str, Any]
    vibration_trend: dict[str, Any]
    trend_summary: dict[str, Any]
    risk_level: str
    possible_causes: list[str]
    recommendations: list[str]

    def to_diagnosis_result(self) -> DiagnosisResult:
        primary = None
        if self.primary_fault and self.primary_fault.get("code"):
            primary = FaultRef(
                code=self.primary_fault["code"],
                description=self.primary_fault.get("description", ""),
            )
        related = [
            FaultRef(code=r["code"], description=r.get("description", ""))
            for r in self.related_faults
            if r.get("code")
        ]
        return DiagnosisResult(
            risk_level=self.risk_level,
            possible_causes=self.possible_causes,
            recommendations=self.recommendations,
            fault_codes=self.fault_codes,
            primary_fault=primary,
            related_faults=related,
            fault_evolution=self.fault_evolution,
            temperature_trend=TrendMetric.from_dict(self.temperature_trend)
            if self.temperature_trend.get("metric")
            else None,
            vibration_trend=TrendMetric.from_dict(self.vibration_trend)
            if self.vibration_trend.get("metric")
            else None,
        )

    def execution_snapshot(self) -> dict[str, Any]:
        return {
            "log_entries": self.log_entries,
            "fault_codes": self.fault_codes,
            "parsed_data": self.parsed_data,
            "fault_code": self.fault_code,
            "primary_fault": self.primary_fault,
            "related_faults": self.related_faults,
            "fault_evolution": self.fault_evolution,
            "trend_summary": self.trend_summary,
            "temperature_trend": self.temperature_trend,
            "vibration_trend": self.vibration_trend,
            "risk_level": self.risk_level,
            "possible_causes": self.possible_causes,
            "recommendations": self.recommendations,
        }


def _boost_risk_from_trends(risk_level: str, trend_summary: dict[str, Any]) -> str:
    temp_dir = (trend_summary.get("temperature") or {}).get("direction")
    vib_dir = (trend_summary.get("vibration") or {}).get("direction")
    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    if temp_dir == "rising" or vib_dir == "rising":
        if order.get(risk_level, 0) < 1:
            risk_level = "MEDIUM"
        if temp_dir == "rising" and vib_dir == "rising" and order.get(risk_level, 0) < 2:
            risk_level = "HIGH"
    return risk_level


def analyze_timeline(
    log_text: str,
    request_fault_code: str | None = None,
) -> TimelineDiagnosisOutput:
    """Parse logs[] / timeline text and produce full timeline diagnosis fields."""
    entries = TimelineParser().parse(log_text)
    log_entries = [e.to_dict() for e in entries]
    fault_codes = collect_fault_codes(entries)
    snapshot = snapshot_from_entries(entries)

    if not snapshot.get("temperature") and not snapshot.get("vibration"):
        legacy = LogParser().parse(log_text)
        for field in ("temperature", "pressure", "rpm", "vibration", "fault_code"):
            val = getattr(legacy, field, None)
            if val is not None and field not in snapshot:
                snapshot[field] = val
        if not fault_codes and legacy.fault_code:
            fault_codes = [legacy.fault_code]
            snapshot["fault_code"] = legacy.fault_code

    parsed_data = {k: v for k, v in snapshot.items() if v is not None}
    fault_code = resolve_fault_code(
        request_fault_code,
        str(fault_codes[-1]) if fault_codes else parsed_data.get("fault_code"),
    )
    if fault_code:
        parsed_data["fault_code"] = fault_code

    trend_summary = build_trend_summary(entries)
    primary = select_primary_fault(fault_codes, entries, request_fault_code)
    related = select_related_faults(fault_codes, primary, None)

    params = params_from_parsed(parsed_data)
    risk_level = assess_risk_level(params)
    risk_level = _boost_risk_from_trends(risk_level, trend_summary)

    evolution = build_fault_evolution(fault_codes, trend_summary, risk_level)
    causes: list[str] = []
    if primary:
        causes.append(f"{primary['code']} {primary['description']}")
    for item in related:
        label = f"{item['code']} {item['description']}"
        if label not in causes:
            causes.append(label)
    if not causes:
        causes = resolve_possible_causes(fault_code, params, risk_level)

    recommendations = build_recommendations(causes, params, risk_level)

    return TimelineDiagnosisOutput(
        fault_code=fault_code or (primary or {}).get("code"),
        fault_codes=fault_codes,
        log_entries=log_entries,
        parsed_data=parsed_data,
        primary_fault=primary,
        related_faults=related,
        fault_evolution=evolution,
        temperature_trend=trend_summary["temperature"],
        vibration_trend=trend_summary["vibration"],
        trend_summary=trend_summary,
        risk_level=risk_level,
        possible_causes=causes,
        recommendations=recommendations,
    )
