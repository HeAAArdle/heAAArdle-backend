from datetime import datetime, timedelta

def get_time_until_end_of_day() -> timedelta:
    """
    Calculates the timedelta until the end of the current day.
    """

    # Get the current datetime
    now = datetime.now() # In format YYYY-MM-DD HH:MM:SS

    # Calculate the start of tomorrow (midnight tonight)
    tomorrow_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())

    # Get the difference
    time_remaining = tomorrow_midnight - now

    return time_remaining

def calculate_time_in_minutes(timedelta: timedelta) -> int:
    """
    Converts a timedelta to total minutes.
    """
    return int(timedelta.total_seconds() // 60)