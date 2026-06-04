"""Execute tools from a plan with timing and error handling."""

import time
from typing import Any

from app.tools.base import ToolContext, ToolResult
from app.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute_one(
        self,
        tool_name: str,
        payload: dict[str, Any],
        context: ToolContext,
    ) -> ToolResult:
        tool = self._registry.get(tool_name)
        started = time.perf_counter()
        try:
            result = tool.run(payload, context)
            result.duration_ms = round((time.perf_counter() - started) * 1000, 2)
            return result
        except Exception as exc:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            return ToolResult(
                tool_name=tool_name,
                input=payload,
                output={},
                status="error",
                duration_ms=duration_ms,
                error=str(exc),
            )

    def execute_plan(
        self,
        plan: list[dict[str, Any]],
        context: ToolContext,
    ) -> list[ToolResult]:
        results: list[ToolResult] = []
        for step in plan:
            name = step.get("tool") or step.get("name")
            if not name:
                continue
            payload = step.get("input") or {}
            results.append(self.execute_one(name, payload, context))
        return results
