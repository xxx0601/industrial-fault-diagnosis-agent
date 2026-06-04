"""Work order domain model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    device_id: str
    fault_type: str
    risk_level: str
    status: str
    diagnosis_id: str | None
    created_at: datetime
