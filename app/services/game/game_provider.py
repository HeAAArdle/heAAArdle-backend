# standard library
from datetime import date as DateType

# SQLAlchemy
from sqlalchemy import select

from sqlalchemy.orm import Session

# models
from app.models import *

# exceptions
from app.services.exceptions import DailyGameNotFound


def get_daily_game(db: Session, date: DateType) -> DailyGame:
    """
    Retrieve the daily game configuration for a specific date.

    Raises:
        DailyGameNotFound: If no daily game exists for the given date.
    """

    # Query the database for the daily game on the specified date
    query = select(DailyGame).where(DailyGame.date == date)

    daily_game = db.scalars(query).first()

    if not daily_game:
        raise DailyGameNotFound()

    return daily_game
