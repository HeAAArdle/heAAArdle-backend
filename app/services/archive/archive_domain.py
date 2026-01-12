# standard library
from datetime import date as DateType

from typing import List

# models
from app.models import *

# schemas
from app.schemas.game import (
    AvailableDay,
    Day,
    UnavailableDay,
)


def create_days_list(
    year: int,
    month: int,
    number_of_days: int,
    daily_game_sessions: dict[DateType, "GameSession"],
) -> List[Day]:
    """
    Build a complete list of Day objects for a given calendar month.

    Each day is represented as either AvailableDay if a session exists or UnavailableDay if no session exists.
    """

    days: List[Day] = []

    # Iterate through all calendar days in the month
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
