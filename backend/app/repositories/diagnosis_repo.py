"""Diagnosis session persistence — JSON index now, PostgreSQL later."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.agent.trace.mapper import legacy_strings_to_steps
from app.models.diagnosis_record import DiagnosisRecord
from app.models.diagnosis_result import DiagnosisResult, FaultRef, TrendMetric
from app.models.trace_step import TraceStep


class DiagnosisRepository:
    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path

    def ensure_ready(self) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._index_path.write_text("[]", encoding="utf-8")

    def add(self, record: DiagnosisRecord) -> DiagnosisRecord:
        items = self._read_raw()
        items.append(self._to_dict(record))
        self._write_raw(items)
        return record

    def get(self, diagnosis_id: str) -> DiagnosisRecord | None:
        for record in self.list_all():
            if record.diagnosis_id == diagnosis_id:
                return record
        return None

    def list_all(self) -> list[DiagnosisRecord]:
        return sorted(
            [self._from_dict(item) for item in self._read_raw()],
            key=lambda r: r.created_at,
            reverse=True,
        )

    def _read_raw(self) -> list[dict]:
        self.ensure_ready()
        data = json.loads(self._index_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Diagnosis index must be a JSON array")
        return data

    def _write_raw(self, items: list[dict]) -> None:
        self._index_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _to_dict(record: DiagnosisRecord) -> dict:
        return {
            "diagnosis_id": record.diagnosis_id,
            "file_id": record.file_id,
            "fault_code": record.fault_code,
            "diagnosis_result": _diagnosis_result_to_dict(record.diagnosis_result),
            "trace": [_trace_to_dict(step) for step in record.trace],
            "execution_meta": record.execution_meta,
            "created_at": record.created_at.isoformat(),
        }

    @staticmethod
    def _from_dict(data: dict) -> DiagnosisRecord:
        result_data = data.get("diagnosis_result")
        if result_data:
            diagnosis_result = _diagnosis_result_from_dict(result_data)
        else:
            diagnosis_result = DiagnosisResult(
                risk_level=data["risk_level"],
                possible_causes=list(data["possible_causes"]),
                recommendations=list(data["recommendations"]),
            )

        trace = _parse_trace(data)
        return DiagnosisRecord(
            diagnosis_id=data["diagnosis_id"],
            file_id=data["file_id"],
            fault_code=data.get("fault_code"),
            diagnosis_result=diagnosis_result,
            trace=trace,
            created_at=datetime.fromisoformat(data["created_at"]),
            execution_meta=dict(data.get("execution_meta") or {}),
        )


def _diagnosis_result_to_dict(result: DiagnosisResult) -> dict:
    payload: dict[str, Any] = {
        "risk_level": result.risk_level,
        "possible_causes": result.possible_causes,
        "recommendations": result.recommendations,
        "fault_codes": result.fault_codes,
        "fault_evolution": result.fault_evolution,
    }
    if result.primary_fault:
        payload["primary_fault"] = {
            "code": result.primary_fault.code,
            "description": result.primary_fault.description,
        }
    payload["related_faults"] = [
        {"code": r.code, "description": r.description} for r in result.related_faults
    ]
    if result.temperature_trend:
        payload["temperature_trend"] = _trend_to_dict(result.temperature_trend)
    if result.vibration_trend:
        payload["vibration_trend"] = _trend_to_dict(result.vibration_trend)
    return payload


def _diagnosis_result_from_dict(data: dict) -> DiagnosisResult:
    primary = data.get("primary_fault")
    primary_ref = None
    if primary and primary.get("code"):
        primary_ref = FaultRef(
            code=str(primary["code"]),
            description=str(primary.get("description", "")),
        )
    related = [
        FaultRef(code=str(r["code"]), description=str(r.get("description", "")))
        for r in data.get("related_faults") or []
        if r.get("code")
    ]
    temp = data.get("temperature_trend")
    vib = data.get("vibration_trend")
    return DiagnosisResult(
        risk_level=data["risk_level"],
        possible_causes=list(data.get("possible_causes") or []),
        recommendations=list(data.get("recommendations") or []),
        fault_codes=list(data.get("fault_codes") or []),
        primary_fault=primary_ref,
        related_faults=related,
        fault_evolution=list(data.get("fault_evolution") or []),
        temperature_trend=TrendMetric.from_dict(temp) if temp else None,
        vibration_trend=TrendMetric.from_dict(vib) if vib else None,
    )


def _trend_to_dict(trend: TrendMetric) -> dict:
    return {
        "metric": trend.metric,
        "direction": trend.direction,
        "from": trend.from_value,
        "to": trend.to_value,
        "delta": trend.delta,
    }


def _trace_to_dict(step: TraceStep) -> dict:
    payload: dict[str, Any] = {
        "step": step.step,
        "node": step.node,
        "message": step.message,
        "status": step.status,
        "metadata": step.metadata,
    }
    if step.started_at:
        payload["started_at"] = step.started_at.isoformat()
    if step.ended_at:
        payload["ended_at"] = step.ended_at.isoformat()
    return payload


def _parse_trace(data: dict) -> list[TraceStep]:
    raw = data.get("trace") or []
    if not raw:
        return []
    if isinstance(raw[0], str):
        return legacy_strings_to_steps(raw)
    return [_trace_from_dict(item) for item in raw]


def _trace_from_dict(item: dict) -> TraceStep:
    started_at = item.get("started_at")
    ended_at = item.get("ended_at")
    return TraceStep(
        step=int(item["step"]),
        node=item["node"],
        message=item["message"],
        status=item.get("status", "success"),
        started_at=datetime.fromisoformat(started_at) if started_at else None,
        ended_at=datetime.fromisoformat(ended_at) if ended_at else None,
        metadata=dict(item.get("metadata") or {}),
    )
