from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User
from sqlalchemy.orm import Session

from app.schemas.account import GetUserStatisticsResponse
from app.services.statistics.statistics_get import get_db_statistics
from app.services.statistics.statistics_map import stat_mapper
from app.services.authentication.authentication_dependencies import get_current_user
from app.db.session import get_db

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