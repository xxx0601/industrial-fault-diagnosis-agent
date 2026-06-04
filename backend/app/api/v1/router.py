from fastapi import APIRouter

from app.api.v1 import diagnosis, health, knowledge, uploads

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(uploads.router, tags=["uploads"])
api_router.include_router(knowledge.router, tags=["knowledge"])
api_router.include_router(diagnosis.router, tags=["diagnosis"])
