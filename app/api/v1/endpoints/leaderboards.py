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
from app.schemas.game import (
    GetLeaderboardDataDaily,
    GetLeaderboardDataOriginal,
    GetLeaderboardDataResponse,
    UserWins,
)

from app.schemas.enums import GameMode, Period

# services
from app.services.leaderboards.leaderboards_get import (
    get_db_leaderboard,
    get_db_user_leaderboard_ranking,
)

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

    user_id = user.userID if user else None

    try:
        # Original: fetch top users for daily, weekly, monthly, and all-time periods
        original_daily = get_db_leaderboard(db, GameMode.ORIGINAL, Period.DAILY)
        original_weekly = get_db_leaderboard(db, GameMode.ORIGINAL, Period.WEEKLY)
        original_monthly = get_db_leaderboard(db, GameMode.ORIGINAL, Period.MONTHLY)
        original_all_time = get_db_leaderboard(db, GameMode.ORIGINAL, Period.ALL_TIME)

        # Daily: fetch top users for weekly, monthly, and all-time periods
        daily_weekly = get_db_leaderboard(db, GameMode.DAILY, Period.WEEKLY)
        daily_monthly = get_db_leaderboard(db, GameMode.DAILY, Period.MONTHLY)
        daily_all_time = get_db_leaderboard(db, GameMode.DAILY, Period.ALL_TIME)

        if user_id:
            # Fetch the authenticated user's rank for each mode and period combination
            rankings = {
                (GameMode.ORIGINAL, Period.DAILY): get_db_user_leaderboard_ranking(
                    db, user_id, GameMode.ORIGINAL, Period.DAILY
                ),
                (GameMode.ORIGINAL, Period.WEEKLY): get_db_user_leaderboard_ranking(
                    db, user_id, GameMode.ORIGINAL, Period.WEEKLY
                ),
                (GameMode.ORIGINAL, Period.MONTHLY): get_db_user_leaderboard_ranking(
                    db, user_id, GameMode.ORIGINAL, Period.MONTHLY
                ),
                (GameMode.ORIGINAL, Period.ALL_TIME): get_db_user_leaderboard_ranking(
                    db, user_id, GameMode.ORIGINAL, Period.ALL_TIME
                ),
                (GameMode.DAILY, Period.WEEKLY): get_db_user_leaderboard_ranking(
                    db, user_id, GameMode.DAILY, Period.WEEKLY
                ),
                (GameMode.DAILY, Period.MONTHLY): get_db_user_leaderboard_ranking(
                    db, user_id, GameMode.DAILY, Period.MONTHLY
                ),
                (GameMode.DAILY, Period.ALL_TIME): get_db_user_leaderboard_ranking(
                    db, user_id, GameMode.DAILY, Period.ALL_TIME
                ),
            }

            # Attach the user's rank to each UserWins entry if applicable
            def attach_rank(
                users: list[UserWins], mode: GameMode, period: Period
            ) -> list[UserWins]:
                rank = rankings.get((mode, period))

                # Update each UserWins with userRank if it matches the authenticated user
                return [
                    UserWins(
                        **user.model_dump(),
                        userRank=rank if user.username == user.username else None
                    )
                    for user in users
                ]

            # Apply user rank to Original mode leaderboards
            original_daily = attach_rank(
                original_daily, GameMode.ORIGINAL, Period.DAILY
            )
            original_weekly = attach_rank(
                original_weekly, GameMode.ORIGINAL, Period.WEEKLY
            )
            original_monthly = attach_rank(
                original_monthly, GameMode.ORIGINAL, Period.MONTHLY
            )
            original_all_time = attach_rank(
                original_all_time, GameMode.ORIGINAL, Period.ALL_TIME
            )

            # Apply user rank to Original mode leaderboards
            daily_weekly = attach_rank(
                daily_weekly, GameMode.DAILY, Period.WEEKLY
            )
            daily_monthly = attach_rank(
                daily_monthly, GameMode.DAILY, Period.MONTHLY
            )
            daily_all_time = attach_rank(
                daily_all_time, GameMode.DAILY, Period.ALL_TIME
            )

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
