"""Build structured trace steps for mock agent and future LangGraph runs."""

from app.agent.trace.mapper import (
    NODE_ANALYZE_TRENDS,
    NODE_FAULT_ANALYSIS,
    NODE_FAULT_TIMELINE,
    NODE_GENERATE_DIAGNOSIS,
    NODE_PARSE_SENSORS,
    NODE_PARSE_TIMELINE,
    NODE_READ_LOG,
    NODE_RISK_EVALUATION,
)
from app.models.device_params import DeviceParams
from app.models.diagnosis_result import DiagnosisResult
from app.models.trace_step import TraceStep

STATUS_SUCCESS = "success"


class TraceBuilder:
    """Accumulates TraceStep during diagnosis; LangGraph adapter will append similarly."""

    def __init__(self) -> None:
        self._steps: list[TraceStep] = []
        self._counter = 0

    @property
    def steps(self) -> list[TraceStep]:
        return list(self._steps)

    def add(
        self,
        node: str,
        message: str,
        *,
        status: str = STATUS_SUCCESS,
        metadata: dict | None = None,
    ) -> TraceStep:
        self._counter += 1
        step = TraceStep(
            step=self._counter,
            node=node,
            message=message,
            status=status,
            metadata=metadata or {},
        )
        self._steps.append(step)
        return step

    def record_read_log(self, file_id: str, line_count: int) -> TraceStep:
        return self.add(
            NODE_READ_LOG,
            "读取日志文件",
            metadata={
                "file_id": file_id,
                "line_count": line_count,
                "node_label": "Read Log",
            },
        )

    def record_parse_timeline(
        self,
        *,
        entry_count: int,
        fault_codes: list[str],
        parsed_data: dict,
    ) -> TraceStep:
        msg = (
            f"解析时间线 {entry_count} 条，识别故障码 {', '.join(fault_codes)}"
            if fault_codes
            else f"解析时间线 {entry_count} 条，未发现故障码"
        )
        return self.add(
            NODE_PARSE_TIMELINE,
            msg,
            metadata={
                "entry_count": entry_count,
                "fault_codes": fault_codes,
                "parsed_data": parsed_data,
                "node_label": "Parse Timeline",
            },
        )

    def record_analyze_trends(self, trend_summary: dict) -> TraceStep:
        temp = (trend_summary.get("temperature") or {}).get("direction", "unknown")
        vib = (trend_summary.get("vibration") or {}).get("direction", "unknown")
        return self.add(
            NODE_ANALYZE_TRENDS,
            f"温振趋势：温度 {temp}，振动 {vib}",
            metadata={"trends": trend_summary, "node_label": "Analyze Trends"},
        )

    def record_fault_timeline(
        self,
        *,
        primary: dict | None,
        related: list[dict],
        evolution: list[str],
    ) -> TraceStep:
        if primary:
            msg = f"主要故障 {primary.get('code')} {primary.get('description')}"
        else:
            msg = "未确定主要故障"
        return self.add(
            NODE_FAULT_TIMELINE,
            msg,
            metadata={
                "primary_fault": primary,
                "related_faults": related,
                "fault_evolution": evolution,
                "node_label": "Fault Timeline",
            },
        )

    def record_parse_params(self, params: DeviceParams) -> TraceStep:
        parsed = {
            k: v
            for k, v in {
                "temperature": params.temperature,
                "pressure": params.pressure,
                "rpm": params.rpm,
                "vibration": params.vibration,
                "fault_code": params.fault_code,
            }.items()
            if v is not None
        }
        return self.add(
            NODE_PARSE_SENSORS,
            "解析设备参数",
            metadata={"params": parsed, "node_label": "Parse Sensor Data"},
        )

    def record_fault_analysis(self, fault_code: str | None) -> TraceStep:
        msg = f"识别故障码 {fault_code}" if fault_code else "未识别到故障码"
        return self.add(
            NODE_FAULT_ANALYSIS,
            msg,
            metadata={"fault_code": fault_code, "node_label": "Fault Analysis"},
        )

    def record_risk_evaluation(self, result: DiagnosisResult) -> TraceStep:
        return self.add(
            NODE_RISK_EVALUATION,
            f"评估风险等级 {result.risk_level}",
            metadata={
                "risk_level": result.risk_level,
                "node_label": "Risk Evaluation",
            },
        )

    def record_generate_diagnosis(self, result: DiagnosisResult) -> TraceStep:
        metadata: dict = {
            "possible_causes": result.possible_causes,
            "recommendations": result.recommendations,
            "node_label": "Generate Diagnosis",
        }
        if result.fault_codes:
            metadata["fault_codes"] = result.fault_codes
        if result.primary_fault:
            metadata["primary_fault"] = {
                "code": result.primary_fault.code,
                "description": result.primary_fault.description,
            }
        if result.related_faults:
            metadata["related_faults"] = [
                {"code": r.code, "description": r.description}
                for r in result.related_faults
            ]
        if result.fault_evolution:
            metadata["fault_evolution"] = result.fault_evolution
        return self.add(NODE_GENERATE_DIAGNOSIS, "生成维修建议", metadata=metadata)
