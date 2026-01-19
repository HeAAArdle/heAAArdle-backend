# standard library
import random

# models
from app.models import *

# schemas
from app.schemas.enums import GameMode

# utils
from app.utils.constants import (
    MODE_AUDIO_CLIP_LENGTH,
    MODE_MAXIMUM_ATTEMPTS,
    MODE_EXPIRES_IN_MINUTES,
)

from app.utils.helpers import (
    calculate_time_in_minutes,
    get_time_until_end_of_day,
)


def get_audio_start_at_by_game_mode(mode: GameMode, song_duration: int) -> int:
    """
    Compute a valid random starting position (in seconds) for a game mode's audio clip.

    Ensures the audio clip fits within the song's duration.
    """

    # Length of the audio clip for the specified game mode
    clip_length = MODE_AUDIO_CLIP_LENGTH[mode]

    # Maximum valid starting point so the clip does not exceed the song duration
    maximum_start_at = max(0, song_duration - clip_length)

    return random.randint(0, maximum_start_at)


def get_maximum_attempts_by_game_mode(mode: GameMode) -> int:
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

    return maximum_attempts


def get_expires_in_minutes_by_game_mode(mode: GameMode) -> int:
    """
    Determine the session expiration time (in minutes) for a given game mode.

    Daily sessions expire at the end of the current day; other modes use predefined durations.
    """

    if mode == GameMode.DAILY:
        # Daily sessions expire at the end of the current day
        return calculate_time_in_minutes(get_time_until_end_of_day())

    else:
        # Non-daily sessions utilize a predefined expiration duration
        return MODE_EXPIRES_IN_MINUTES[mode]
