from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_upload_service
from app.schemas.upload import UploadListResponse, UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads")


@router.post("", response_model=UploadResponse)
async def upload_device_log(
    file: UploadFile = File(..., description="Device log file (.txt, .csv, .json)"),
    service: UploadService = Depends(get_upload_service),
) -> UploadResponse:
    return await service.create_upload(file)


@router.get("", response_model=UploadListResponse)
def list_device_logs(
    service: UploadService = Depends(get_upload_service),
) -> UploadListResponse:
    items = service.list_uploads()
    return UploadListResponse(items=items, total=len(items))
