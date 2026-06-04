"""Tool: lookup fault code definition and severity."""

from typing import Any

from app.tools.base import ToolContext, ToolResult
from app.tools.schemas import QueryFaultCodeInput, QueryFaultCodeOutput

_FAULT_DB: dict[str, dict[str, str]] = {
    "E101": {"description": "电机过载", "severity": "MEDIUM"},
    "E204": {"description": "主轴过热", "severity": "HIGH"},
    "E305": {"description": "冷却系统异常", "severity": "MEDIUM"},
    "E410": {"description": "轴承磨损", "severity": "HIGH"},
}


class QueryFaultCodeTool:
    name = "query_fault_code"
    description = "Query fault code manual for description and severity"

    def run(self, payload: dict[str, Any], context: ToolContext) -> ToolResult:
        _ = context
        inp = QueryFaultCodeInput.model_validate(payload)
        code = inp.fault_code.strip().upper()
        entry = _FAULT_DB.get(
            code,
            {"description": "未知故障码", "severity": "LOW"},
        )
        out = QueryFaultCodeOutput(
            fault_code=code,
            description=entry["description"],
            severity=entry["severity"],
        )
        return ToolResult(
            tool_name=self.name,
            input=inp.model_dump(),
            output=out.model_dump(),
        )
