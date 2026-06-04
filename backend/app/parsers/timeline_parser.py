"""Parse device logs into an ordered timeline (JSON logs[] or text lines)."""

import json
import re
from typing import Any

from app.models.log_entry import LogEntry
from app.parsers.fault_code_extractor import (
    extract_fault_code_from_token,
    is_normal_status,
    normalize_fault_code,
)
from app.parsers.log_parser import LogParser, _FIELD_ALIASES

# 08:00 NORMAL  |  09:00 E101  |  2024-01-01 09:00:00 E101
_TIMELINE_LINE = re.compile(
    r"^\s*(?:(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(?::\d{2})?)|(\d{1,2}:\d{2}(?::\d{2})?))\s+(.+?)\s*$"
)


class TimelineParser:
    """Build ordered log entries from full log text."""

    def parse(self, text: str) -> list[LogEntry]:
        stripped = text.strip()
        if not stripped:
            return []

        if stripped.startswith("{") or stripped.startswith("["):
            entries = self._parse_json(stripped)
            if entries:
                return entries

        return self._parse_text_lines(text)

    def _parse_json(self, text: str) -> list[LogEntry]:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return []

        if isinstance(data, dict):
            logs = data.get("logs")
            if isinstance(logs, list):
                return self._entries_from_dicts(logs)
            return self._entries_from_dicts([data])

        if isinstance(data, list):
            if data and all(isinstance(item, dict) for item in data):
                return self._entries_from_dicts(data)
            return []

        return []

    def _entries_from_dicts(self, items: list[dict[str, Any]]) -> list[LogEntry]:
        entries: list[LogEntry] = []
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            entries.append(self._entry_from_mapping(idx, item))
        return entries

    def _entry_from_mapping(self, index: int, data: dict[str, Any]) -> LogEntry:
        timestamp = _first_str(
            data,
            "timestamp",
            "time",
            "ts",
            "datetime",
            "recorded_at",
        )
        status = _first_str(data, "status", "state", "level")
        fault_code = normalize_fault_code(
            _first_str(data, "fault_code", "fault", "error_code", "code")
        )
        if not fault_code:
            for key in ("message", "event", "status"):
                val = data.get(key)
                if isinstance(val, str):
                    fault_code = extract_fault_code_from_token(val)
                    if fault_code:
                        break

        temperature = pressure = rpm = vibration = None
        for key, value in data.items():
            alias = _FIELD_ALIASES.get(key.strip().lower().replace("_", " "))
            if alias == "temperature":
                temperature = _to_float(value)
            elif alias == "pressure":
                pressure = _to_float(value)
            elif alias == "rpm":
                rpm = _to_float(value)
            elif alias == "vibration":
                vibration = _to_float(value)
            elif alias == "fault_code" and not fault_code:
                fault_code = normalize_fault_code(str(value))

        if not status and fault_code:
            status = fault_code
        elif not status and is_normal_status(str(data.get("status", ""))):
            status = "NORMAL"

        return LogEntry(
            index=index,
            timestamp=timestamp,
            status=status,
            fault_code=fault_code,
            temperature=temperature,
            pressure=pressure,
            rpm=rpm,
            vibration=vibration,
            raw=dict(data),
        )

    def _parse_text_lines(self, text: str) -> list[LogEntry]:
        entries: list[LogEntry] = []
        idx = 0
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entry = self._parse_timeline_line(idx, line)
            if entry:
                entries.append(entry)
                idx += 1
        return entries

    def _parse_timeline_line(self, index: int, line: str) -> LogEntry | None:
        match = _TIMELINE_LINE.match(line)
        if match:
            ts = match.group(1) or match.group(2)
            remainder = match.group(3).strip()
            return self._entry_from_remainder(index, ts, remainder)

        # Fallback: bare fault code or key=value lines via LogParser snapshot fields
        code = extract_fault_code_from_token(line)
        if code:
            return LogEntry(index=index, fault_code=code, status=code)
        return None

    def _entry_from_remainder(
        self, index: int, timestamp: str, remainder: str
    ) -> LogEntry:
        parts = remainder.split()
        status: str | None = None
        fault_code: str | None = None
        temperature = vibration = pressure = rpm = None

        for part in parts:
            code = extract_fault_code_from_token(part)
            if code:
                fault_code = code
                status = code
                continue
            if is_normal_status(part):
                status = "NORMAL"
                continue
            kv_temp = _parse_inline_metric(part, "temp", "temperature")
            if kv_temp is not None:
                temperature = kv_temp
            kv_vib = _parse_inline_metric(part, "vib", "vibration")
            if kv_vib is not None:
                vibration = kv_vib

        if not fault_code and not is_normal_status(status):
            fault_code = extract_fault_code_from_token(remainder)
            if fault_code:
                status = fault_code

        return LogEntry(
            index=index,
            timestamp=timestamp,
            status=status or ("NORMAL" if is_normal_status(remainder) else remainder),
            fault_code=fault_code,
            temperature=temperature,
            vibration=vibration,
            pressure=pressure,
            rpm=rpm,
            raw={"line": remainder},
        )


def collect_fault_codes(entries: list[LogEntry]) -> list[str]:
    """Unique fault codes in order of first appearance."""
    seen: set[str] = set()
    result: list[str] = []
    for entry in entries:
        if entry.fault_code and entry.fault_code not in seen:
            seen.add(entry.fault_code)
            result.append(entry.fault_code)
    return result


def snapshot_from_entries(entries: list[LogEntry]) -> dict[str, float | str]:
    """Last known sensor values and last fault code across the timeline."""
    snapshot: dict[str, float | str] = {}
    for entry in entries:
        if entry.temperature is not None:
            snapshot["temperature"] = entry.temperature
        if entry.pressure is not None:
            snapshot["pressure"] = entry.pressure
        if entry.rpm is not None:
            snapshot["rpm"] = entry.rpm
        if entry.vibration is not None:
            snapshot["vibration"] = entry.vibration
        if entry.fault_code:
            snapshot["fault_code"] = entry.fault_code

    if not snapshot and entries:
        parser = LogParser()
        # No structured entries — let legacy parser fill scalars from full text join
        pass
    return snapshot


def _first_str(data: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        val = data.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return None


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_inline_metric(token: str, *prefixes: str) -> float | None:
    lower = token.lower()
    for prefix in prefixes:
        if lower.startswith(prefix):
            num = re.sub(r"[^\d.]", "", token[len(prefix) :])
            try:
                return float(num)
            except ValueError:
                return None
    if "=" in token or ":" in token:
        sep = "=" if "=" in token else ":"
        key, val = token.split(sep, 1)
        if key.strip().lower() in prefixes:
            try:
                return float(val.strip())
            except ValueError:
                return None
    return None
