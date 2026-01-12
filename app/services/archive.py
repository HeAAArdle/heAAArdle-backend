# standard library
import calendar

from datetime import date as DateType

from typing import List, cast

# SQLAlchemy
from sqlalchemy import select, func

from sqlalchemy.orm import Session

# models
from app.models.game_session import GameSession

# schemas
from app.schemas.game import (
    AvailableDay,
    Day,
    GetArchivedDailyGameResultsResponse,
    UnavailableDay,
)

# exceptions
from app.services.exceptions import InvalidYearOrMonth

"""
Validators
"""


def validate_year_and_month(year: int, month: int) -> tuple[int, int]:
    """
    Validates the given year and month.

    Returns (first_weekday, number_of_days) for the given month.

    Raises ValueError if the either the year or month is invalid.
    """

    try:
        return calendar.monthrange(year, month)

    except Exception:
        raise InvalidYearOrMonth()


"""
Getters
"""


def get_daily_game_sessions_by_user_month(
    db: Session, user_id: str, year: int, month: int
) -> dict[DateType, GameSession]:
    """
    Retrieves all game sessions for a user within a given year and month.

    Returns a dictionary {DateType: GameSession}.
    """

    query = (
        select(GameSession)
        .where(GameSession.userID == user_id)
        .where(func.extract("year", GameSession.date) == year)
        .where(func.extract("month", GameSession.date) == month)
    )

    results = db.scalars(query).all()

    return cast(
        dict[DateType, GameSession],
        {daily_game.date: daily_game for daily_game in results},
    )


"""
Others
"""


def create_days_list(
    year: int,
    month: int,
    number_of_days: int,
    daily_game_sessions: dict[DateType, "GameSession"],
) -> List[Day]:
    """
    Builds a complete list of Day objects for a given calendar month.
    """

    days: List[Day] = []

    # Iterate through every calendar day in the month
    for day in range(1, number_of_days + 1):

        current_date = DateType(year, month, day)

        # Days with a game session are marked as available
        if current_date in daily_game_sessions:
            daily_game = daily_game_sessions[current_date]

            # Normalize the stored game result into a boolean outcome
            mapping = {"win": True, "lose": False}

            result = mapping.get(daily_game.result)

            days.append(AvailableDay(date=current_date, available=True, result=result))

        # Days without a corresponding game session are unavailable
        else:
            days.append(UnavailableDay(date=current_date, available=False, result=None))

    return days


"""
Mains
"""


def get_archived_daily_game_results_service(
    year: int,
    month: int,
    db: Session,
    user_id: str,
) -> GetArchivedDailyGameResultsResponse:
    """
    Gets the archived daily game results for a user for a given month.
    """

    # Validate year and month
    starting_day, number_of_days = validate_year_and_month(year, month)

    # Get all game sessions for the user within the month
    daily_game_sessions = get_daily_game_sessions_by_user_month(
        db, user_id, year, month
    )

    # Build the list of days with availability and results
    days = create_days_list(year, month, number_of_days, daily_game_sessions)

    return GetArchivedDailyGameResultsResponse(
        numberOfDays=number_of_days,
        startingDay=starting_day,
        days=days,
    )
