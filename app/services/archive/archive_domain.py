# standard library
from datetime import date as DateType

from typing import List

# models
from app.models import *

# schemas
from app.schemas.archive import (
    AvailableDay,
    Day,
    UnavailableDay,
)


def create_days_list(
    year: int,
    month: int,
    number_of_days: int,
    daily_game_dates: list[DateType],
    daily_game_sessions: dict[DateType, "GameSession"],
) -> List[Day]:
    """
    Build a complete list of Day objects for a given calendar month.

    Each day is represented as either AvailableDay if a daily game exists or UnavailableDay otherwise.
    """

    days: List[Day] = []

    # Map persisted game outcomes to a boolean result
    mapping = {"win": True, "lose": False}

    # Iterate through all calendar days in the month
    for day in range(1, number_of_days + 1):
        current_date = DateType(year, month, day)

        # Check whether a daily game was scheduled for this date
        if current_date in daily_game_dates:
            # Look up the user's session for the date
            daily_game_session = daily_game_sessions.get(current_date)

            # Resolve the user's result

            # None if the user did not participate
            if not daily_game_session:
                result = None

            # True or False if the game was played
            else:
                result = mapping.get(daily_game_session.result)

            days.append(AvailableDay(date=current_date, available=True, result=result))

        # No daily game existed for this date
        else:
            days.append(UnavailableDay(date=current_date, available=False, result=None))

    return days
