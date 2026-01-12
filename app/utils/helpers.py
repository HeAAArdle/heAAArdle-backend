from datetime import datetime, timedelta


def get_time_until_end_of_day() -> timedelta:
    """
    Calculates the remaining time until the end of the current day.
    """

    # Get the current local datetime
    now = datetime.now()  # In format YYYY-MM-DD HH:MM:SS

    # Calculate the start of tomorrow (midnight tonight)
    tomorrow_midnight = datetime.combine(
        now.date() + timedelta(days=1), datetime.min.time()
    )

    # Get the difference
    time_remaining = tomorrow_midnight - now

    return time_remaining


def calculate_time_in_minutes(timedelta: timedelta) -> int:
    """
    Convert a timedelta duration to whole minutes.
    """

    return int(timedelta.total_seconds() // 60)


def calculate_minutes_to_seconds(minutes: int) -> int:
    """
    Convert minutes to seconds.
    """

    return minutes * 60
