import uuid

from datetime import datetime, timedelta

from app.ws.session import GameSession

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

def generate_unique_game_session_id(sessions: dict[str, GameSession]) -> str:
    """
    Generates a unique Websocket game session ID.
    """

    while True:
        session_id = str(uuid.uuid4())

        if session_id not in sessions:
            return session_id