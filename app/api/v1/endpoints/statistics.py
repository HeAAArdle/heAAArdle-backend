# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
from app.db.session import get_db

# models
from app.models.user import User

# schemas
from app.schemas.account import GetUserStatisticsResponse

# services
from app.services.statistics.statistics_get import get_db_statistics

from app.services.statistics.statistics_map import stat_mapper

from app.services.user.user_dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=GetUserStatisticsResponse)
def get_user_statistics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Verifies the user and retrieves their statistics.
    """
    stats = get_db_statistics(db, user.userID)

    original = stats.get("original")
    daily = stats.get("daily")

    if not original or not daily:
        raise HTTPException(status_code=500, detail="Statistics missing")

    return GetUserStatisticsResponse(original=stat_mapper(original), daily=stat_mapper(daily))