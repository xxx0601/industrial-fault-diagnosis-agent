"""Central tool registry — register MCP / custom tools here."""

from dataclasses import dataclass

from app.tools.base import AgentTool
from app.tools.calculate_risk_score import CalculateRiskScoreTool
from app.tools.create_work_order import CreateWorkOrderTool
from app.tools.query_device_status import QueryDeviceStatusTool
from app.tools.query_fault_code import QueryFaultCodeTool


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentTool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(name=t.name, description=t.description) for t in self._tools.values()
        ]


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(QueryFaultCodeTool())
    registry.register(QueryDeviceStatusTool())
    registry.register(CalculateRiskScoreTool())
    registry.register(CreateWorkOrderTool())
    return registry
