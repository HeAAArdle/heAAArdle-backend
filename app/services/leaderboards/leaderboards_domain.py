# standard library
import uuid

from typing import Optional

# SQLAlchemy
from sqlalchemy.orm import Session

# models
from app.models.user import User

from app.models.user__leaderboard import UserLeaderboard

# schemas
from app.schemas.enums import GameMode, Period

from app.schemas.leaderboards import LeaderboardRow

# services
from app.services.leaderboards.leaderboards_provider import (
    get_db_leaderboard,
    get_db_user_leaderboard_ranking,
)


def build_leaderboard(
    db: Session,
    mode: GameMode,
    period: Period,
    user: Optional[User],
    limit: int = 5,
) -> list[LeaderboardRow]:
    """
    Build a leaderboard for a provided game mode and period.

    Includes the top users and, if applicable, the current user's ranking.
    """
    # Retrieve the top users for the given mode and period
    top_users = get_db_leaderboard(db, mode, period, limit)

    leaderboard: list[LeaderboardRow] = []

    # Track whether the current user appears in the top results
    user_in_top = False

    # Populate leaderboard rows from the top users
    for row in top_users:
        # Determine whether this row corresponds to the authenticated user
        is_current_user = user is not None and row.username == user.username

        if is_current_user:
            user_in_top = True

        leaderboard.append(
            LeaderboardRow(
                username=row.username,
                isUser=is_current_user,
                numberOfWins=row.numberOfWins,
            )
        )

    # If the user is authenticated but not in the top list, append their individual ranking at the end
    if user and not user_in_top:
        rank, numberOfWins = get_db_user_leaderboard_ranking(
            db, user.userID, mode, period
        )

        leaderboard.append(
            LeaderboardRow(
                username=user.username,
                isUser=True,
                numberOfWins=numberOfWins,
                rank=rank,
            )
        )

    return leaderboard


def update_leaderboards_after_game(db: Session, user_id: uuid.UUID, mode: GameMode):
    """
    Update the leaderboards for a user after a game has been won.
    """

    if mode == GameMode.ORIGINAL:
        periods = [Period.DAILY, Period.WEEKLY, Period.MONTHLY, Period.ALL_TIME]
    else:
        periods = [Period.WEEKLY, Period.MONTHLY, Period.ALL_TIME]

    for period in periods:
        increment_leaderboard(db, user_id, mode, period)


def increment_leaderboard(db: Session, user_id: uuid.UUID, mode: GameMode, period: str):
    """
    Increment the number of wins for a user in the leaderboard of a specific mode.
    """

    row = (
        db.query(UserLeaderboard)
        .filter(
            UserLeaderboard.userID == user_id,
            UserLeaderboard.mode == mode,
            UserLeaderboard.period == period,
        )
        .first()
    )

    if not row:
        row = UserLeaderboard(userID=user_id, mode=mode, period=period, numberOfWins=1)

        db.add(row)

    else:
        row.numberOfWins += 1
