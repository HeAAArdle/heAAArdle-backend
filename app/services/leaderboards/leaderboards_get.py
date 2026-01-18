from sqlalchemy.orm import Session

from app.models.user__leaderboard import UserLeaderboard
from app.models.user import User

def get_db_leaderboard(db: Session, mode: str, period: str, limit: int = 5):
    """
    Returns top N (5) users for a given mode and period leaderboard.
    """
    rows = (db.query(User.username, UserLeaderboard.numberOfWins)
        .join(User, User.userID == UserLeaderboard.userID)
        .filter(UserLeaderboard.mode == mode, UserLeaderboard.period == period)
        .order_by(UserLeaderboard.numberOfWins.desc())
        .limit(limit)
        .all()
    )

    return [{"username": row.username, "wins": row.numberOfWins} for row in rows]
