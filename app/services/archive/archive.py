# standard library
import uuid

# SQLAlchemy
from sqlalchemy.orm import Session

# schemas
from app.schemas.game import GetArchivedDailyGameResultsResponse

# services
from app.services.archive.archive_domain import create_days_list

from app.services.archive.archive_provider import get_daily_game_sessions_by_user_id_and_month

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

    # Validate year and month
    starting_day, number_of_days = validate_year_and_month(year, month)

    # Get all game sessions for the user within the month
    daily_game_sessions = get_daily_game_sessions_by_user_id_and_month(
        db, user_id, year, month
    )

    # Build the list of days with availability and results
    days = create_days_list(year, month, number_of_days, daily_game_sessions)

    return GetArchivedDailyGameResultsResponse(
        numberOfDays=number_of_days,
        startingDay=starting_day,
        days=days,
    )
