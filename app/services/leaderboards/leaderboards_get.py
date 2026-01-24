from sqlalchemy.orm import Session
from sqlalchemy import func, select
from uuid import UUID

from app.models.user__leaderboard import UserLeaderboard
from app.models.user import User


def get_db_leaderboard(db: Session, mode: str, period: str, limit: int = 5):
    """
    Returns top N (5) users for a given mode and period leaderboard.
    """
    # Query the leaderboard entries
    result = (db.query(User.username, UserLeaderboard.numberOfWins)
        .join(User, User.userID == UserLeaderboard.userID)
        .filter(UserLeaderboard.mode == mode, UserLeaderboard.period == period)
        .order_by(UserLeaderboard.numberOfWins.desc())
        .limit(limit)
        .all()
    )

    return [{"username": row.username, "wins": row.numberOfWins} for row in result]

def get_db_user_leaderboard_ranking(db: Session, user_id: UUID, mode: str, period: str) -> int | None:
    """
    Returns the rank of a user in the specific leaderboard.
    """
    # Sorts the users by number of wins and assigns ranks
    ranked_subquery = (
        select(UserLeaderboard.userID, UserLeaderboard.numberOfWins, 
               func.rank().over(order_by=UserLeaderboard.numberOfWins.desc()).label("rank"),
        )
        .where(UserLeaderboard.mode == mode, UserLeaderboard.period == period)
        .subquery()
    )

    # Query the rank of the specific user
    result = (db.query(ranked_subquery.c.rank).filter(ranked_subquery.c.userID == user_id).first())

    return result.rank if result else None