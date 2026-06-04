"""Rule-based mock agent — fallback when AGENT_BACKEND=mock (timeline-aware)."""

from app.agent.base import AgentDiagnosisResult, AgentRunResult, DiagnosisContext
from app.agent.workflows.timeline import analyze_timeline
from app.agent.trace.builder import TraceBuilder
from app.services.upload_service import UploadService


class MockDiagnosisAgent:
    def run(
        self,
        file_id: str,
        fault_code: str | None,
        upload_service: UploadService,
    ) -> AgentRunResult:
        log_text = upload_service.read_log_content(file_id)
        output = analyze_timeline(log_text, fault_code)
        result = output.to_diagnosis_result()

        builder = TraceBuilder()
        line_count = len([line for line in log_text.splitlines() if line.strip()])
        builder.record_read_log(file_id, line_count)
        builder.record_parse_timeline(
            entry_count=len(output.log_entries),
            fault_codes=output.fault_codes,
            parsed_data=output.parsed_data,
        )
        builder.record_analyze_trends(output.trend_summary)
        builder.record_fault_timeline(
            primary=output.primary_fault,
            related=output.related_faults,
            evolution=output.fault_evolution,
        )
        builder.record_risk_evaluation(result)
        builder.record_generate_diagnosis(result)

        return AgentRunResult(
            fault_code=output.fault_code,
            diagnosis_result=result,
            trace=builder.steps,
            execution_meta={
                "agent_backend": "mock",
                "graph_id": "mock_timeline_v1",
                "final_state": output.execution_snapshot(),
            },
        )

    def diagnose(self, ctx: DiagnosisContext) -> AgentDiagnosisResult:
        output = analyze_timeline(ctx.log_text, ctx.fault_code)
        result = output.to_diagnosis_result()
        return AgentDiagnosisResult(
            risk_level=result.risk_level,
            possible_causes=result.possible_causes,
            recommendations=result.recommendations,
        )
