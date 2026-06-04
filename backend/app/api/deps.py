"""FastAPI dependencies (DB session, auth, services)."""

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.diagnosis_service import DiagnosisService, build_diagnosis_service
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
    build_knowledge_base_service,
)
from app.services.upload_service import UploadService, build_upload_service


def get_app_settings() -> Settings:
    return get_settings()


@lru_cache
def get_upload_service() -> UploadService:
    return build_upload_service(get_settings())


@lru_cache
def get_diagnosis_service() -> DiagnosisService:
    return build_diagnosis_service(get_settings(), get_upload_service())


@lru_cache
def get_knowledge_base_service() -> KnowledgeBaseService:
    return build_knowledge_base_service(get_settings())
