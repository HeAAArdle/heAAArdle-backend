import uuid
from sqlalchemy.orm import Session

from app.models.user__leaderboard import UserLeaderboard


def update_leaderboards_after_game(db: Session, user_id: uuid.UUID, mode: str):
    """
    Updates the leaderboards for a user after a game has been won.
    """
    if mode == "original":
        periods = ["daily", "weekly", "monthly", "allTime"]
    else:
        periods = ["weekly", "monthly", "allTime"]

    for period in periods:
        increment_leaderboard(db, user_id, mode, period)


def increment_leaderboard(db: Session, user_id: uuid.UUID, mode: str, period: str):
    """
    Increments the number of wins for a user in the leaderboard of a specific mode.
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
