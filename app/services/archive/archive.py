# standard library
import uuid

# SQLAlchemy
from sqlalchemy.orm import Session

# schemas
from app.schemas.game import GetArchivedDailyGameResultsResponse

# services
from app.services.archive.archive_domain import create_days_list

from app.services.archive.archive_provider import (
    get_archived_daily_game_dates_by_month,
    get_archived_daily_game_sessions_by_user_id_and_month,
)

from app.services.archive.archive_validator import validate_year_and_month


def get_archived_daily_game_results_service(
    year: int,
    month: int,
    db: Session,
    user_id: uuid.UUID,
) -> GetArchivedDailyGameResultsResponse:
    """
    Gets the archived daily game results for a user for a given month.
    """

    # Validate year and month and get the starting weekday and number of days
    starting_day, number_of_days = validate_year_and_month(year, month)

    # Get previous year and month
    if month == 1:
        # Input month is January
        previous_month = 12
        previous_year = year - 1

    else:
        previous_month = month - 1
        previous_year = year

    # Validate previous year and month and get the number of days
    _, number_of_days_of_previous_month = validate_year_and_month(
        previous_year, previous_month
    )

    # Retrieve all dates in the month where a daily game was available
    daily_game_dates = get_archived_daily_game_dates_by_month(db, year, month)

    # Retrieve daily game sessions played by the user during the month
    daily_game_sessions = get_archived_daily_game_sessions_by_user_id_and_month(
        db, user_id, year, month
    )

    # Construct the per-day availability and result list for the response
    days = create_days_list(
        year, month, number_of_days, daily_game_dates, daily_game_sessions
    )

    return GetArchivedDailyGameResultsResponse(
        numberOfDays=number_of_days,
        numberOfDaysOfPreviousMonth=number_of_days_of_previous_month,
        startingDay=starting_day,
        days=days,
    )
