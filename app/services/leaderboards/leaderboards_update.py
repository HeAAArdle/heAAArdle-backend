# standard library
import uuid

# SQLAlchemy
from sqlalchemy.orm import Session

# models
from app.models.user__leaderboard import UserLeaderboard

# schemas
from app.schemas.enums import GameMode, Period


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
