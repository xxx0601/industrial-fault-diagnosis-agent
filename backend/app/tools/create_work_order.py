"""Tool: create maintenance work order."""

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import ValidationError
from app.models.work_order import WorkOrder
from app.tools.base import ToolContext, ToolResult
from app.tools.schemas import CreateWorkOrderInput, CreateWorkOrderOutput


class CreateWorkOrderTool:
    name = "create_work_order"
    description = "Create a maintenance work order for high-risk faults"

    def run(self, payload: dict[str, Any], context: ToolContext) -> ToolResult:
        inp = CreateWorkOrderInput.model_validate(payload)
        if not context.work_order_repo:
            raise ValidationError("Work order repository not configured")

        work_order_id = str(uuid.uuid4())
        order = WorkOrder(
            work_order_id=work_order_id,
            device_id=inp.device_id,
            fault_type=inp.fault_type,
            risk_level=inp.risk_level,
            status="created",
            diagnosis_id=context.diagnosis_id,
            created_at=datetime.now(UTC),
        )
        context.work_order_repo.add(order)
        out = CreateWorkOrderOutput(work_order_id=work_order_id, status="created")
        return ToolResult(
            tool_name=self.name,
            input=inp.model_dump(),
            output=out.model_dump(),
        )
