"""Tool input/output schemas for validation and OpenAPI/MCP export."""

from pydantic import BaseModel, Field


class QueryFaultCodeInput(BaseModel):
    fault_code: str = Field(..., min_length=1)


class QueryFaultCodeOutput(BaseModel):
    fault_code: str
    description: str
    severity: str


class QueryDeviceStatusInput(BaseModel):
    device_id: str = Field(..., min_length=1)


class QueryDeviceStatusOutput(BaseModel):
    temperature: float
    pressure: float
    rpm: float
    vibration: float


class CalculateRiskScoreInput(BaseModel):
    temperature: float
    pressure: float
    rpm: float
    vibration: float


class CalculateRiskScoreOutput(BaseModel):
    risk_score: int


class CreateWorkOrderInput(BaseModel):
    device_id: str
    fault_type: str
    risk_level: str


class CreateWorkOrderOutput(BaseModel):
    work_order_id: str
    status: str
