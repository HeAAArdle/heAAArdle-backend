from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# attach the health endpoint under /health. the full path will be /api/v1/health
api_router.include_router(health.router, prefix="/health")