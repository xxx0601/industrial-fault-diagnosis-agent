"""Trace API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TraceStepSchema(BaseModel):
    step: int
    node: str
    message: str
    status: str = "success"
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
