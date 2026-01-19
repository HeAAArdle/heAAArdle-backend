# standard library
import uuid

# SQLAlchemy
from sqlalchemy.orm import Session

# schemas
from app.schemas.game import SubmitGameRequest


def update_leaderboard(payload: SubmitGameRequest, db: Session, user_id: uuid.UUID):
    if not payload.won:
        return
