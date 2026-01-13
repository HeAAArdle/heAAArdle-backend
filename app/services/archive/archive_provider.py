# standard library
import uuid

from datetime import date as DateType

# SQLAlchemy
from sqlalchemy import select, func

from sqlalchemy.orm import Session

# models
from app.models import *


def get_daily_game_dates_by_month(
    db: Session,
    year: int,
    month: int,
) -> list[DateType]:
    """
    Retrieve all dates with an available DailyGame for a specific year and month.

    Returns:
        Set of dates where a DailyGame exists.
    """

    # Query dates where a DailyGame exists within the specified year and month
    query = (
        select(DailyGame.date)
        .where(func.extract("year", DailyGame.date) == year)
        .where(func.extract("month", DailyGame.date) == month)
    )

    daily_game_dates = db.scalars(query).all()

    return [date for date in daily_game_dates]


def get_daily_game_sessions_by_user_id_and_month(
    db: Session, user_id: uuid.UUID, year: int, month: int
) -> dict[DateType, GameSession]:
    """
    Retrieve all game sessions for a user within a specific year and month.

    Returns:
        {DateType: GameSession} mapping dates to game sessions for the user.
    """

    # Query all game sessions for the user in the specified year and month
    query = (
        select(GameSession)
        .where(GameSession.userID == user_id)
        .where(func.extract("year", GameSession.date) == year)
        .where(func.extract("month", GameSession.date) == month)
    )

    daily_game_sessions = db.scalars(query).all()

    # Convert list of sessions to a dictionary keyed by date
    return {daily_game.date: daily_game for daily_game in daily_game_sessions}
