"""Domain model for an uploaded device log — maps to DB table in a later step."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UploadRecord:
    file_id: str
    filename: str
    file_type: str
    upload_time: datetime
    stored_name: str
    size_bytes: int
    content_type: str | None = None
