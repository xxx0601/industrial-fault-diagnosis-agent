"""Parsed device parameters extracted from log text."""

from dataclasses import dataclass, field


@dataclass
class DeviceParams:
    temperature: float | None = None
    pressure: float | None = None
    rpm: float | None = None
    vibration: float | None = None
    fault_code: str | None = None
    raw_keys: dict[str, str] = field(default_factory=dict)
