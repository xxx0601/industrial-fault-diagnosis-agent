"""Upload API request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    upload_time: datetime


class UploadListResponse(BaseModel):
    items: list[UploadResponse] = Field(default_factory=list)
    total: int = 0
