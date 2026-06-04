"""Diagnosis orchestration — delegates workflow to Mock or LangGraph agent."""

import uuid
from datetime import UTC, datetime
from pathlib import Path

from app.agent.base import DiagnosisAgentProtocol
from app.agent.registry import get_diagnosis_agent
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.models.diagnosis_record import DiagnosisRecord
from app.models.diagnosis_result import DiagnosisResult, TrendMetric
from app.repositories.diagnosis_repo import DiagnosisRepository
from app.schemas.diagnosis import (
    DiagnosisDetailResponse,
    DiagnosisRequest,
    DiagnosisResponse,
    DiagnosisResultSchema,
    FaultRefSchema,
    RagSourceSummary,
    TrendMetricSchema,
)
from app.schemas.trace import TraceStepSchema
from app.services.upload_service import UploadService

LOG_PREVIEW_MAX_CHARS = 8000


class DiagnosisService:
    def __init__(
        self,
        upload_service: UploadService,
        agent: DiagnosisAgentProtocol,
        repo: DiagnosisRepository,
    ) -> None:
        self._uploads = upload_service
        self._agent = agent
        self._repo = repo

    def ensure_ready(self) -> None:
        self._repo.ensure_ready()

    def run_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResponse:
        record = self._execute_diagnosis(request)
        return self._to_create_response(record)

    def get_diagnosis_detail(self, diagnosis_id: str) -> DiagnosisDetailResponse:
        record = self._repo.get(diagnosis_id)
        if record is None:
            raise NotFoundError(f"Diagnosis not found: {diagnosis_id}")

        log_preview: str | None = None
        try:
            raw = self._uploads.read_log_content(record.file_id)
            log_preview = self._trim_log_preview(raw)
        except NotFoundError:
            log_preview = None

        return DiagnosisDetailResponse(
            diagnosis_id=record.diagnosis_id,
            file_id=record.file_id,
            fault_code=record.fault_code,
            created_at=record.created_at,
            diagnosis_result=self._result_to_schema(record.diagnosis_result),
            trace=[self._trace_to_schema(step) for step in record.trace],
            log_preview=log_preview,
            rag_sources=self._extract_rag_sources(record.execution_meta),
            tool_results=self._extract_tool_results(record.execution_meta),
            risk_score=self._extract_risk_score(record.execution_meta),
            work_order_id=self._extract_work_order_id(record.execution_meta),
            log_entries=self._extract_log_entries(record.execution_meta),
        )

    @staticmethod
    def _extract_tool_results(execution_meta: dict) -> list[dict]:
        final_state = execution_meta.get("final_state") or {}
        raw = final_state.get("tool_results") or execution_meta.get("tool_results") or []
        return list(raw) if isinstance(raw, list) else []

    @staticmethod
    def _extract_risk_score(execution_meta: dict) -> int | None:
        final_state = execution_meta.get("final_state") or {}
        score = final_state.get("risk_score")
        return int(score) if score is not None else None

    @staticmethod
    def _extract_work_order_id(execution_meta: dict) -> str | None:
        final_state = execution_meta.get("final_state") or {}
        wid = final_state.get("work_order_id")
        return str(wid) if wid else None

    @staticmethod
    def _extract_rag_sources(execution_meta: dict) -> list[RagSourceSummary]:
        final_state = execution_meta.get("final_state") or {}
        chunks = final_state.get("rag_chunks") or execution_meta.get("rag_chunks") or []
        sources: list[RagSourceSummary] = []
        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue
            sources.append(
                RagSourceSummary(
                    doc_id=str(chunk.get("doc_id", "")),
                    doc_name=chunk.get("doc_name"),
                    chunk_text=str(chunk.get("chunk_text", "")),
                    similarity_score=float(chunk.get("similarity_score", 0)),
                )
            )
        return sources

    def _execute_diagnosis(self, request: DiagnosisRequest) -> DiagnosisRecord:
        agent_output = self._agent.run(
            file_id=request.file_id,
            fault_code=request.fault_code,
            upload_service=self._uploads,
        )

        diagnosis_id = str(uuid.uuid4())
        record = DiagnosisRecord(
            diagnosis_id=diagnosis_id,
            file_id=request.file_id,
            fault_code=agent_output.fault_code,
            diagnosis_result=agent_output.diagnosis_result,
            trace=agent_output.trace,
            created_at=datetime.now(UTC),
            execution_meta=agent_output.execution_meta,
        )
        self._repo.add(record)
        return record

    @staticmethod
    def _extract_log_entries(execution_meta: dict) -> list[dict]:
        final_state = execution_meta.get("final_state") or {}
        entries = final_state.get("log_entries") or []
        return list(entries) if isinstance(entries, list) else []

    @staticmethod
    def _trend_to_schema(trend: TrendMetric | None) -> TrendMetricSchema | None:
        if trend is None:
            return None
        return TrendMetricSchema(
            metric=trend.metric,
            direction=trend.direction,
            from_value=trend.from_value,
            to_value=trend.to_value,
            delta=trend.delta,
        )

    @staticmethod
    def _result_to_schema(result: DiagnosisResult) -> DiagnosisResultSchema:
        primary = None
        if result.primary_fault:
            primary = FaultRefSchema(
                code=result.primary_fault.code,
                description=result.primary_fault.description,
            )
        return DiagnosisResultSchema(
            risk_level=result.risk_level,
            possible_causes=result.possible_causes,
            recommendations=result.recommendations,
            fault_codes=result.fault_codes,
            primary_fault=primary,
            related_faults=[
                FaultRefSchema(code=r.code, description=r.description)
                for r in result.related_faults
            ],
            fault_evolution=result.fault_evolution,
            temperature_trend=DiagnosisService._trend_to_schema(result.temperature_trend),
            vibration_trend=DiagnosisService._trend_to_schema(result.vibration_trend),
        )

    @staticmethod
    def _to_create_response(record: DiagnosisRecord) -> DiagnosisResponse:
        result = record.diagnosis_result
        schema = DiagnosisService._result_to_schema(result)
        return DiagnosisResponse(
            diagnosis_id=record.diagnosis_id,
            risk_level=schema.risk_level,
            possible_causes=schema.possible_causes,
            recommendations=schema.recommendations,
            fault_codes=schema.fault_codes,
            primary_fault=schema.primary_fault,
            related_faults=schema.related_faults,
            fault_evolution=schema.fault_evolution,
            temperature_trend=schema.temperature_trend,
            vibration_trend=schema.vibration_trend,
            trace=[
                DiagnosisService._trace_to_schema(step) for step in record.trace
            ],
        )

    @staticmethod
    def _trace_to_schema(step) -> TraceStepSchema:
        return TraceStepSchema(
            step=step.step,
            node=step.node,
            message=step.message,
            status=step.status,
            started_at=step.started_at,
            ended_at=step.ended_at,
            metadata=step.metadata,
        )

    @staticmethod
    def _trim_log_preview(text: str) -> str:
        if len(text) <= LOG_PREVIEW_MAX_CHARS:
            return text
        return text[:LOG_PREVIEW_MAX_CHARS] + "\n\n… (truncated)"


def build_diagnosis_service(settings: Settings, upload_service: UploadService) -> DiagnosisService:
    repo = DiagnosisRepository(Path(settings.diagnosis_index_path).resolve())
    return DiagnosisService(
        upload_service=upload_service,
        agent=get_diagnosis_agent(),
        repo=repo,
    )
