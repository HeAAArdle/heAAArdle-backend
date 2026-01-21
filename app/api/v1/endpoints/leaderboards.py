from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.game import (
    GetLeaderboardDataResponse,
    GetLeaderboardDataOriginal,
    GetLeaderboardDataDaily,
    UserWins,
)
from app.services.leaderboards.leaderboards_get import get_db_leaderboard

router = APIRouter()


@router.get("/", response_model=GetLeaderboardDataResponse)
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Returns leaderboard winners for all modes and periods.
    """

    # Helper function to map database rows to UserWins schema.
    def map_users(data):
        return [UserWins(**row) for row in data]

    # Original Mode in all periods
    original_daily = map_users(get_db_leaderboard(db, "original", "daily"))
    original_weekly = map_users(get_db_leaderboard(db, "original", "weekly"))
    original_monthly = map_users(get_db_leaderboard(db, "original", "monthly"))
    original_all_time = map_users(get_db_leaderboard(db, "original", "all_time"))

    # Daily Mode in all periods
    daily_weekly = map_users(get_db_leaderboard(db, "daily", "weekly"))
    daily_monthly = map_users(get_db_leaderboard(db, "daily", "monthly"))
    daily_all_time = map_users(get_db_leaderboard(db, "daily", "all_time"))

    return GetLeaderboardDataResponse(
        original=GetLeaderboardDataOriginal(
            daily=original_daily,
            weekly=original_weekly,
            monthly=original_monthly,
            allTime=original_all_time,
        ),
        daily=GetLeaderboardDataDaily(
            weekly=daily_weekly,
            monthly=daily_monthly,
            allTime=daily_all_time,
        ),
    )
