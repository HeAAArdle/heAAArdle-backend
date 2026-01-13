from fastapi import APIRouter
from app.api.v1.endpoints import health, statistics, user

api_router = APIRouter()

# attach the health endpoint under /health. the full path will be /api/v1/health
api_router.include_router(health.router, prefix="/health")
api_router.include_router(statistics.router, prefix="/statistics")
api_router.include_router(user.router, prefix="/user")