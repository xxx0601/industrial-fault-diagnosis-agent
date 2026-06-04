"""Agent tool contracts — extensible for MCP and multi-agent."""

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.repositories.work_order_repo import WorkOrderRepository
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.upload_service import UploadService


@dataclass
class ToolContext:
    file_id: str
    device_id: str | None = None
    parsed_data: dict[str, Any] = field(default_factory=dict)
    fault_code: str | None = None
    upload_service: UploadService | None = None
    knowledge_service: KnowledgeBaseService | None = None
    work_order_repo: WorkOrderRepository | None = None
    diagnosis_id: str | None = None


@dataclass
class ToolResult:
    tool_name: str
    input: dict[str, Any]
    output: dict[str, Any]
    status: str = "success"
    duration_ms: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "input": self.input,
            "output": self.output,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


class AgentTool(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    def run(self, payload: dict[str, Any], context: ToolContext) -> ToolResult: ...
