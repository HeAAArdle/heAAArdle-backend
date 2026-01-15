from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(title="HeAAArdle")

# Take all the routes inside api_router and make them available under /api/v1
app.include_router(api_router, prefix="/api/v1")