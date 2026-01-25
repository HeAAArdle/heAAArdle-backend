# standard library
from typing import Optional

# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
from app.db.session import get_db

# schemas
from app.models.user import User

from app.schemas.leaderboards import (
    GetLeaderboardDataDaily,
    GetLeaderboardDataOriginal,
    GetLeaderboardDataResponse,
)

from app.schemas.enums import GameMode, Period

# services
from app.services.leaderboards.leaderboards_get import build_leaderboard

from app.services.user.user_dependencies import get_optional_user

# exceptions
from app.services.exceptions import LimitIsBelow1, UserNotOnLeaderboard

router = APIRouter()


@router.get("/", response_model=GetLeaderboardDataResponse)
def get_leaderboard(
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve leaderboard winners for all game modes and periods.

    If a user is authenticated, their personal rank is included in the results.
    """

    try:
        # Original: fetch top users for daily, weekly, monthly, and all-time periods
        original_daily = build_leaderboard(db, GameMode.ORIGINAL, Period.DAILY, user)
        original_weekly = build_leaderboard(db, GameMode.ORIGINAL, Period.WEEKLY, user)
        original_monthly = build_leaderboard(db, GameMode.ORIGINAL, Period.MONTHLY, user)
        original_all_time = build_leaderboard(db, GameMode.ORIGINAL, Period.ALL_TIME, user)

        # Daily: fetch top users for weekly, monthly, and all-time periods
        daily_weekly = build_leaderboard(db, GameMode.DAILY, Period.WEEKLY, user)
        daily_monthly = build_leaderboard(db, GameMode.DAILY, Period.MONTHLY, user)
        daily_all_time = build_leaderboard(db, GameMode.DAILY, Period.ALL_TIME, user)

    except LimitIsBelow1:
        raise HTTPException(400, "Limit must be a positive integer.")

    except UserNotOnLeaderboard:
        raise HTTPException(404, "User does not have an associated leaderboard entry.")

    # Return all leaderboard data
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
