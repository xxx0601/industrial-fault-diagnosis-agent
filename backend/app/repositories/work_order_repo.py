"""Work order persistence — JSON index."""

import json
from datetime import datetime
from pathlib import Path

from app.models.work_order import WorkOrder


class WorkOrderRepository:
    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path

    def ensure_ready(self) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._index_path.write_text("[]", encoding="utf-8")

    def add(self, order: WorkOrder) -> WorkOrder:
        items = self._read_raw()
        items.append(self._to_dict(order))
        self._write_raw(items)
        return order

    def get(self, work_order_id: str) -> WorkOrder | None:
        for order in self.list_all():
            if order.work_order_id == work_order_id:
                return order
        return None

    def list_all(self) -> list[WorkOrder]:
        return sorted(
            [self._from_dict(item) for item in self._read_raw()],
            key=lambda o: o.created_at,
            reverse=True,
        )

    def _read_raw(self) -> list[dict]:
        self.ensure_ready()
        data = json.loads(self._index_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []

    def _write_raw(self, items: list[dict]) -> None:
        self._index_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _to_dict(order: WorkOrder) -> dict:
        return {
            "work_order_id": order.work_order_id,
            "device_id": order.device_id,
            "fault_type": order.fault_type,
            "risk_level": order.risk_level,
            "status": order.status,
            "diagnosis_id": order.diagnosis_id,
            "created_at": order.created_at.isoformat(),
        }

    @staticmethod
    def _from_dict(data: dict) -> WorkOrder:
        return WorkOrder(
            work_order_id=data["work_order_id"],
            device_id=data["device_id"],
            fault_type=data["fault_type"],
            risk_level=data["risk_level"],
            status=data["status"],
            diagnosis_id=data.get("diagnosis_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
