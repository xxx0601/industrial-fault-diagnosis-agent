"""Shared deterministic rules — used by Mock agent and LangGraph nodes."""

from app.models.device_params import DeviceParams

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

_FAULT_CAUSES: dict[str, list[str]] = {
    "E101": ["电机过载"],
    "E204": ["主轴过热"],
    "E305": ["冷却系统异常"],
    "E410": ["轴承磨损"],
}

_CAUSE_RECOMMENDATIONS: dict[str, list[str]] = {
    "电机过载": ["检查电机负载", "检查电源"],
    "主轴过热": ["检查冷却系统", "检查风扇"],
    "冷却系统异常": ["检查冷却液", "检查水泵"],
    "轴承磨损": ["检查轴承"],
}

_PARAM_RECOMMENDATIONS: dict[str, list[str]] = {
    "temperature": ["检查冷却系统", "检查风扇"],
    "vibration": ["检查轴承", "检查设备安装"],
}


def params_from_parsed(parsed_data: dict) -> DeviceParams:
    return DeviceParams(
        temperature=parsed_data.get("temperature"),
        pressure=parsed_data.get("pressure"),
        rpm=parsed_data.get("rpm"),
        vibration=parsed_data.get("vibration"),
        fault_code=parsed_data.get("fault_code"),
    )


def resolve_fault_code(request_code: str | None, parsed_code: str | None) -> str | None:
    if request_code:
        return request_code.strip().upper()
    return parsed_code


def assess_risk_level(params: DeviceParams) -> str:
    levels: list[str] = [RISK_LOW]
    if params.temperature is not None:
        if params.temperature > 90:
            levels.append(RISK_HIGH)
        elif params.temperature > 80:
            levels.append(RISK_MEDIUM)
    if params.vibration is not None:
        if params.vibration > 8:
            levels.append(RISK_HIGH)
        elif params.vibration > 5:
            levels.append(RISK_MEDIUM)
    return _max_risk(levels)


def resolve_causes_from_fault_code(fault_code: str | None) -> list[str]:
    if fault_code and fault_code in _FAULT_CAUSES:
        return list(_FAULT_CAUSES[fault_code])
    return []


def resolve_possible_causes(
    fault_code: str | None,
    params: DeviceParams,
    risk_level: str,
) -> list[str]:
    causes: list[str] = []
    if fault_code and fault_code in _FAULT_CAUSES:
        causes.extend(_FAULT_CAUSES[fault_code])
    if not causes and risk_level != RISK_LOW:
        if params.temperature is not None and params.temperature > 80:
            causes.append("温度异常")
        if params.vibration is not None and params.vibration > 5:
            causes.append("振动异常")
    if not causes:
        causes.append("未发现明显异常")
    return _dedupe(causes)


def build_recommendations(
    causes: list[str],
    params: DeviceParams,
    risk_level: str,
) -> list[str]:
    recs: list[str] = []
    for cause in causes:
        recs.extend(_CAUSE_RECOMMENDATIONS.get(cause, []))
    if risk_level in (RISK_MEDIUM, RISK_HIGH):
        if params.temperature is not None and params.temperature > 80:
            recs.extend(_PARAM_RECOMMENDATIONS["temperature"])
        if params.vibration is not None and params.vibration > 5:
            recs.extend(_PARAM_RECOMMENDATIONS["vibration"])
    if not recs:
        recs = ["继续监测设备运行状态"]
    return _dedupe(recs)


def _max_risk(levels: list[str]) -> str:
    order = {RISK_LOW: 0, RISK_MEDIUM: 1, RISK_HIGH: 2}
    return max(levels, key=lambda level: order.get(level, 0))


def merge_rag_recommendations(
    base: list[str],
    rag_chunks: list[dict],
    *,
    max_snippets: int = 3,
) -> list[str]:
    recs = list(base)
    for chunk in rag_chunks[:max_snippets]:
        text = (chunk.get("chunk_text") or "").strip()
        doc = chunk.get("doc_name") or chunk.get("doc_id") or "知识库"
        if not text:
            continue
        snippet = text.replace("\n", " ")[:120]
        recs.append(f"参考《{doc}》: {snippet}…")
    return _dedupe(recs)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
