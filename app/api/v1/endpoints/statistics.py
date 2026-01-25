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

from app.schemas.enums import GameMode

# services
from app.services.statistics.statistics_get import get_db_statistics

from app.services.statistics.statistics_map import stat_mapper

from app.services.user.user_dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=GetUserStatisticsResponse)
def get_user_statistics(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Retrieve statistics for the authenticated user.

    Verifies the user and fetches their statistics for each game mode.
    """
    # Fetch raw statistics from the database for the user
    stats = get_db_statistics(db, user.userID)

    # Extract statistics for Original and Daily game modes
    original = stats.get(GameMode.ORIGINAL)

    daily = stats.get(GameMode.DAILY)

    # Ensure that statistics exist for both modes
    if not original or not daily:
        raise HTTPException(status_code=500, detail="Statistics missing.")

    return GetUserStatisticsResponse(
        original=stat_mapper(original), daily=stat_mapper(daily)
    )
