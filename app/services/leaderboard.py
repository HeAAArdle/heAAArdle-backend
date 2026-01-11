from sqlalchemy.orm import Session

from app.schemas.game import SubmitGameRequest


def update_leaderboard(db: Session, payload: SubmitGameRequest):
    if not payload.won:
        return
