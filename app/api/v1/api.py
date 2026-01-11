from fastapi import APIRouter
from app.api.v1.websockets import game
from app.api.v1.endpoints import health
from app.api.v1.endpoints import songs
from app.api.v1.endpoints import start
from app.api.v1.endpoints import submit
from app.api.v1.endpoints import archive

api_router = APIRouter()

# attach the health endpoint under /health. the full path will be /api/v1/health
api_router.include_router(health.router, prefix="/health")

api_router.include_router(game.router, prefix="/ws/game")

api_router.include_router(songs.router, prefix="/")

api_router.include_router(start.router, prefix="/game")

api_router.include_router(submit.router, prefix="/game")

api_router.include_router(archive.router, prefix="/archive")
