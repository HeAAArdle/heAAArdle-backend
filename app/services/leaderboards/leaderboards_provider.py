# standard library
from uuid import UUID

# SQLAlchemy
from sqlalchemy import func, select

from sqlalchemy.orm import Session

# models
from app.models.user import User

from app.models.user__leaderboard import UserLeaderboard

# schemas
from app.schemas.leaderboards import LeaderboardRow

from app.schemas.enums import GameMode, Period

# exceptions
from app.services.exceptions import LimitIsBelow1, UserNotOnLeaderboard


def get_db_leaderboard(
    db: Session, mode: GameMode, period: Period, limit: int = 5
) -> list[LeaderboardRow]:
    """
    Retrieve the top users for a specific game mode and period.

    Returns:
        A list of LeaderboardRow objects containing usernames and win counts.
    """

    # Validate that the row limit is at least 1
    if limit <= 0:
        raise LimitIsBelow1()

    # Query the leaderboard, joining with the User table to get usernames

    # Filter by the requested mode and period

    # Order by number of wins descending and limit the results by the input
    query = (
        select(User.username, UserLeaderboard.numberOfWins)
        .join(User, User.userID == UserLeaderboard.userID)
        .where(UserLeaderboard.mode == mode, UserLeaderboard.period == period)
        .order_by(UserLeaderboard.numberOfWins.desc())
        .limit(limit)
    )

    rows = db.execute(query).all()

    # Convert query results into a list of LeaderboardRow
    return [
        LeaderboardRow(username=row.username, numberOfWins=row.numberOfWins)
        for row in rows
    ]


def get_db_user_leaderboard_ranking(
    db: Session, user_id: UUID, mode: GameMode, period: Period
) -> tuple[int, int]:
    """
    Retrieve the rank and win count of a specific user within a leaderboard for a mode and period.

    Returns:
        A tuple of (rank, numberOfWins).

    Raises:
        UserNotOnLeaderboard: If the user has no leaderboard entry.
    """

    # Generate a subquery that ranks all users by number of wins in descending order
    ranked_subquery = (
        select(
            UserLeaderboard.userID,
            UserLeaderboard.numberOfWins,
            func.rank()
            .over(order_by=UserLeaderboard.numberOfWins.desc())
            .label("rank"),
        )
        .where(UserLeaderboard.mode == mode, UserLeaderboard.period == period)
        .subquery()
    )

    # Query the rank and number of wins of the specified user from the subquery
    result = (
        db.query(
            ranked_subquery.c.rank,
            ranked_subquery.c.numberOfWins,
        )
        .filter(ranked_subquery.c.userID == user_id)
        .first()
    )

    # Validate that the user has a corresponding leaderboard entry
    if result is None:
        raise UserNotOnLeaderboard()

    return result.rank, result.numberOfWins
