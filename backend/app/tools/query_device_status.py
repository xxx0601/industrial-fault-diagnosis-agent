"""Tool: query live or log-derived device sensor readings."""

from typing import Any

from app.tools.base import ToolContext, ToolResult
from app.tools.schemas import QueryDeviceStatusInput, QueryDeviceStatusOutput

# Mock live telemetry when log lacks fields
_DEFAULT_TELEMETRY = {
    "temperature": 72.0,
    "pressure": 20.0,
    "rpm": 3000.0,
    "vibration": 3.5,
}


class QueryDeviceStatusTool:
    name = "query_device_status"
    description = "Query current device temperature, pressure, RPM, and vibration"

    def run(self, payload: dict[str, Any], context: ToolContext) -> ToolResult:
        inp = QueryDeviceStatusInput.model_validate(payload)
        parsed = context.parsed_data or {}
        values = {
            "temperature": float(parsed.get("temperature", _DEFAULT_TELEMETRY["temperature"])),
            "pressure": float(parsed.get("pressure", _DEFAULT_TELEMETRY["pressure"])),
            "rpm": float(parsed.get("rpm", _DEFAULT_TELEMETRY["rpm"])),
            "vibration": float(parsed.get("vibration", _DEFAULT_TELEMETRY["vibration"])),
        }
        if context.upload_service and context.file_id:
            try:
                text = context.upload_service.read_log_content(context.file_id)
                from app.parsers.log_parser import LogParser

                params = LogParser().parse(text)
                if params.temperature is not None:
                    values["temperature"] = params.temperature
                if params.pressure is not None:
                    values["pressure"] = params.pressure
                if params.rpm is not None:
                    values["rpm"] = params.rpm
                if params.vibration is not None:
                    values["vibration"] = params.vibration
            except Exception:
                pass

        out = QueryDeviceStatusOutput(**values)
        return ToolResult(
            tool_name=self.name,
            input=inp.model_dump(),
            output=out.model_dump(),
        )
