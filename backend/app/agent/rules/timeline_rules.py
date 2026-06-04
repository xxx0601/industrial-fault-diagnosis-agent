"""Timeline analysis: trends, primary/related faults, evolution chain."""

from typing import Any

from app.models.log_entry import LogEntry

# Higher number = higher priority when picking primary among multiple codes
_FAULT_PRIORITY: dict[str, int] = {
    "E410": 100,
    "E204": 80,
    "E305": 60,
    "E101": 40,
}

_FAULT_DESCRIPTIONS: dict[str, str] = {
    "E101": "电机过载",
    "E204": "主轴过热",
    "E305": "冷却系统异常",
    "E410": "轴承磨损",
}

# Evolution steps keyed by presence of fault codes (ordered narrative)
_EVOLUTION_BY_CODE: dict[str, str] = {
    "E410": "轴承磨损",
    "E204": "主轴过热",
    "E305": "冷却系统负载增加",
    "E101": "电机过载",
}

_TREND_RISING_THRESHOLD = 0.5
_TREND_FALLING_THRESHOLD = -0.5


def analyze_metric_trend(
    entries: list[LogEntry],
    field: str,
) -> dict[str, Any]:
    """Compute direction and endpoints for temperature or vibration series."""
    values: list[tuple[str | None, float]] = []
    for entry in entries:
        val = getattr(entry, field, None)
        if val is not None:
            values.append((entry.timestamp, float(val)))

    if not values:
        return {
            "metric": field,
            "direction": "unknown",
            "from": None,
            "to": None,
            "delta": None,
            "points": [],
        }

    points = [{"time": t, "value": v} for t, v in values]
    start_val = values[0][1]
    end_val = values[-1][1]
    delta = end_val - start_val

    if len(values) < 2:
        direction = "stable"
    elif delta >= _TREND_RISING_THRESHOLD:
        direction = "rising"
    elif delta <= _TREND_FALLING_THRESHOLD:
        direction = "falling"
    else:
        direction = "stable"

    return {
        "metric": field,
        "direction": direction,
        "from": start_val,
        "to": end_val,
        "delta": round(delta, 3),
        "points": points,
    }


def build_trend_summary(entries: list[LogEntry]) -> dict[str, Any]:
    temp = analyze_metric_trend(entries, "temperature")
    vib = analyze_metric_trend(entries, "vibration")
    return {
        "temperature": temp,
        "vibration": vib,
    }


def select_primary_fault(
    fault_codes: list[str],
    entries: list[LogEntry],
    request_code: str | None,
) -> dict[str, str] | None:
    if request_code:
        code = request_code.strip().upper()
        return {"code": code, "description": _description_for(code)}

    if not fault_codes:
        return None

    # Last non-normal fault on timeline
    last_code: str | None = None
    for entry in reversed(entries):
        if entry.fault_code:
            last_code = entry.fault_code
            break

    if last_code:
        return {"code": last_code, "description": _description_for(last_code)}

    # Fallback: highest priority among collected codes
    best = max(fault_codes, key=lambda c: _FAULT_PRIORITY.get(c, 0))
    return {"code": best, "description": _description_for(best)}


def select_related_faults(
    fault_codes: list[str],
    primary: dict[str, str] | None,
    fault_lookup: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    primary_code = (primary or {}).get("code")
    lookup = fault_lookup or {}
    related: list[dict[str, str]] = []
    for code in fault_codes:
        if code == primary_code:
            continue
        desc = lookup.get(code) or _description_for(code)
        related.append({"code": code, "description": desc})
    return related


def build_fault_evolution(
    fault_codes: list[str],
    trend_summary: dict[str, Any],
    risk_level: str = "LOW",
) -> list[str]:
    """Build causal evolution narrative (wear → vibration → heat → cooling load)."""
    steps: list[str] = []
    codes = set(fault_codes)

    if "E410" in codes:
        steps.append(_EVOLUTION_BY_CODE["E410"])

    vib = trend_summary.get("vibration") or {}
    if vib.get("direction") == "rising":
        steps.append("振动升高")

    if "E204" in codes:
        steps.append(_EVOLUTION_BY_CODE["E204"])

    if "E305" in codes:
        steps.append(_EVOLUTION_BY_CODE["E305"])

    if "E101" in codes and len(codes) == 1:
        steps.append(_EVOLUTION_BY_CODE["E101"])

    if not steps:
        chain_order = ["E101", "E305", "E204", "E410"]
        for code in chain_order:
            if code in fault_codes:
                steps.append(_EVOLUTION_BY_CODE[code])

    if risk_level == "HIGH":
        steps.append("设备进入高风险状态")
    elif not steps:
        steps.append("设备运行正常")

    return _dedupe_preserve(steps)


def merge_fault_descriptions(
    tool_results: list[dict[str, Any]] | None,
) -> dict[str, str]:
    lookup: dict[str, str] = dict(_FAULT_DESCRIPTIONS)
    for item in tool_results or []:
        if not isinstance(item, dict):
            continue
        out = item.get("output") or {}
        if item.get("tool_name") == "query_fault_code" or out.get("fault_code"):
            code = str(out.get("fault_code", "")).upper()
            desc = out.get("description")
            if code and desc:
                lookup[code] = str(desc)
    return lookup


def _description_for(code: str) -> str:
    return _FAULT_DESCRIPTIONS.get(code.upper(), "未知故障")


def _dedupe_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
