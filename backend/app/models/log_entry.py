"""Structured log entry for timeline-based diagnosis."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogEntry:
    """One point on the device log timeline."""

    index: int
    timestamp: str | None = None
    status: str | None = None
    fault_code: str | None = None
    temperature: float | None = None
    pressure: float | None = None
    rpm: float | None = None
    vibration: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "status": self.status,
            "fault_code": self.fault_code,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "rpm": self.rpm,
            "vibration": self.vibration,
            "raw": self.raw,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LogEntry":
        return cls(
            index=int(data.get("index", 0)),
            timestamp=data.get("timestamp"),
            status=data.get("status"),
            fault_code=data.get("fault_code"),
            temperature=_as_float(data.get("temperature")),
            pressure=_as_float(data.get("pressure")),
            rpm=_as_float(data.get("rpm")),
            vibration=_as_float(data.get("vibration")),
            raw=dict(data.get("raw") or {}),
        )


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
