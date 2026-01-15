from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router

from app.core.config import settings

app = FastAPI(title="HeAAArdle")

assert settings.frontend_url is not None, "Missing frontend URL in .env."

# CORS (Cross-Origin Resource Sharing) middleware configuration
origins = [
    settings.frontend_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Take all the routes inside api_router and make them available under /api/v1
app.include_router(api_router, prefix="/api/v1")