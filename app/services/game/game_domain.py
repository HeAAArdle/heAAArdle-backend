# standard library
import random

from datetime import date as DateType

# SQLAlchemy
from sqlalchemy import select

from sqlalchemy.orm import Session

# models
from app.models import *

# exceptions
from app.services.exceptions import DailyGameNotFound

# utils
from app.utils.constants import (
    MODE_AUDIO_CLIP_LENGTH,
    MODE_EXPIRES_IN,
)

from app.utils.helpers import (
    calculate_time_in_minutes,
    get_time_until_end_of_day,
)


def get_daily_game(db: Session, date: DateType) -> DailyGame:
    """
    Retrieve the daily game configuration for a specific date.

    Raises:
        DailyGameNotFound: If no daily game exists for the given date.
    """

    # Query the database for the daily game on the specified date
    query = select(DailyGame).where(DailyGame.date == date)

    daily_game = db.scalars(query).first()

    if not daily_game:
        raise DailyGameNotFound()

    return daily_game


def get_start_at_by_game_mode(mode: str, song_duration: int) -> int:
    """
    Compute a valid random starting position (in seconds) for a game mode's audio clip.

    Ensures the audio clip fits within the song's duration.
    """

    # Length of the audio clip for the specified game mode
    clip_length = MODE_AUDIO_CLIP_LENGTH[mode]

    # Maximum valid starting point so the clip does not exceed the song duration
    maximum_start_at = max(0, song_duration - clip_length)

    return random.randint(0, maximum_start_at)


def get_expires_in_by_game_mode(mode: str) -> int:
    """
    Determine the session expiration time (in minutes) for a given game mode.

    Daily sessions expire at the end of the current day; other modes use predefined durations.
    """

    if mode == "daily":
        # Daily sessions expire at the end of the current day
        return calculate_time_in_minutes(get_time_until_end_of_day())
    else:
        # Non-daily sessions utilize a predefined expiration duration
        return MODE_EXPIRES_IN[mode]
