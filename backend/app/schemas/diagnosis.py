"""Diagnosis API schemas."""



from datetime import datetime



from pydantic import BaseModel, Field



from app.schemas.trace import TraceStepSchema





class DiagnosisRequest(BaseModel):

    file_id: str = Field(..., min_length=1)

    fault_code: str | None = Field(default=None, description="Optional; overrides log fault code")





class FaultRefSchema(BaseModel):

    code: str

    description: str





class TrendMetricSchema(BaseModel):

    metric: str

    direction: str

    from_value: float | None = Field(default=None, alias="from")

    to_value: float | None = Field(default=None, alias="to")

    delta: float | None = None



    model_config = {"populate_by_name": True}





class DiagnosisResultSchema(BaseModel):

    risk_level: str

    possible_causes: list[str]

    recommendations: list[str]

    fault_codes: list[str] = Field(default_factory=list)

    primary_fault: FaultRefSchema | None = None

    related_faults: list[FaultRefSchema] = Field(default_factory=list)

    fault_evolution: list[str] = Field(default_factory=list)

    temperature_trend: TrendMetricSchema | None = None

    vibration_trend: TrendMetricSchema | None = None





class DiagnosisResponse(BaseModel):

    """POST /diagnosis — compact create response."""



    diagnosis_id: str

    risk_level: str

    possible_causes: list[str]

    recommendations: list[str]

    trace: list[TraceStepSchema]

    fault_codes: list[str] = Field(default_factory=list)

    primary_fault: FaultRefSchema | None = None

    related_faults: list[FaultRefSchema] = Field(default_factory=list)

    fault_evolution: list[str] = Field(default_factory=list)

    temperature_trend: TrendMetricSchema | None = None

    vibration_trend: TrendMetricSchema | None = None





class RagSourceSummary(BaseModel):

    doc_id: str

    doc_name: str | None = None

    chunk_text: str

    similarity_score: float





class DiagnosisDetailResponse(BaseModel):

    """GET /diagnosis/{id} — full detail for Trace UI."""



    diagnosis_id: str

    file_id: str

    fault_code: str | None = None

    created_at: datetime

    diagnosis_result: DiagnosisResultSchema

    trace: list[TraceStepSchema]

    log_preview: str | None = None

    rag_sources: list[RagSourceSummary] = Field(default_factory=list)

    tool_results: list[dict] = Field(default_factory=list)

    risk_score: int | None = None

    work_order_id: str | None = None

    log_entries: list[dict] = Field(default_factory=list)

