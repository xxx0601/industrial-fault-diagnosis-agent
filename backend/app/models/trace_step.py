"""Structured agent trace step — maps to LangGraph node execution records."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TraceStep:
    step: int
    node: str
    message: str
    status: str = "success"
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
