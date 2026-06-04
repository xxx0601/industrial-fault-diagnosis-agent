from fastapi import APIRouter, Depends

from app.api.deps import get_diagnosis_service
from app.schemas.diagnosis import (
    DiagnosisDetailResponse,
    DiagnosisRequest,
    DiagnosisResponse,
)
from app.services.diagnosis_service import DiagnosisService

router = APIRouter(prefix="/diagnosis")


@router.post("", response_model=DiagnosisResponse)
def create_diagnosis(
    body: DiagnosisRequest,
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> DiagnosisResponse:
    return service.run_diagnosis(body)


@router.get("/{diagnosis_id}", response_model=DiagnosisDetailResponse)
def get_diagnosis_detail(
    diagnosis_id: str,
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> DiagnosisDetailResponse:
    return service.get_diagnosis_detail(diagnosis_id)
