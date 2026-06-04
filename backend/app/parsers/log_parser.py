"""Parse device parameters from uploaded log text (txt/csv/json-like lines)."""

import json
import re
from typing import Any

from app.models.device_params import DeviceParams

# Temperature: 96  |  temperature=96  |  "temperature": 96
_KV_PATTERN = re.compile(
    r"(?i)^\s*([a-z][a-z0-9_\s]*?)\s*[:=]\s*([^\s,;]+)\s*$"
)

_FIELD_ALIASES: dict[str, str] = {
    "temperature": "temperature",
    "temp": "temperature",
    "pressure": "pressure",
    "rpm": "rpm",
    "vibration": "vibration",
    "fault code": "fault_code",
    "fault_code": "fault_code",
    "faultcode": "fault_code",
    "error code": "fault_code",
    "error_code": "fault_code",
}


class LogParser:
    def parse(self, text: str) -> DeviceParams:
        params = DeviceParams()
        stripped = text.strip()

        if stripped.startswith("{") or stripped.startswith("["):
            self._apply_json(stripped, params)

        for line in text.splitlines():
            self._apply_line(line, params)

        return params

    def _apply_json(self, text: str, params: DeviceParams) -> None:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return
        if isinstance(data, dict):
            self._apply_mapping(data, params)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._apply_mapping(item, params)

    def _apply_mapping(self, data: dict[str, Any], params: DeviceParams) -> None:
        for key, value in data.items():
            normalized = _FIELD_ALIASES.get(key.strip().lower().replace("_", " "))
            if not normalized:
                continue
            self._set_field(params, normalized, value)

    def _apply_line(self, line: str, params: DeviceParams) -> None:
        match = _KV_PATTERN.match(line.strip())
        if not match:
            return
        raw_key, raw_value = match.group(1).strip(), match.group(2).strip()
        alias = _FIELD_ALIASES.get(raw_key.lower())
        if alias:
            self._set_field(params, alias, raw_value)
        params.raw_keys[raw_key] = raw_value

    def _set_field(self, params: DeviceParams, field: str, value: Any) -> None:
        if field == "fault_code":
            params.fault_code = str(value).strip().upper()
            return
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return
        setattr(params, field, numeric)
