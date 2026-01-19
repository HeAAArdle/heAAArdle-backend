# standard library
import calendar

# exceptions
from app.services.exceptions import InvalidYearOrMonth


def validate_year_and_month(year: int, month: int) -> tuple[int, int]:
    """
    Validate the specified year and month.

    Returns:
        (first_weekday, number_of_days) for the given month.

    Raises:
        InvalidYearOrMonth: If the year or month is invalid.
    """

    try:
        return calendar.monthrange(year, month)

    except calendar.IllegalMonthError:
        raise InvalidYearOrMonth()
