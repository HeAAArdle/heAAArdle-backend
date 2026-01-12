# standard library
import random

import uuid

from datetime import date as DateType

from typing import Optional

# SQLAlchemy
from sqlalchemy import select

from sqlalchemy.orm import Session

# models
from app.models.daily_game import DailyGame

from app.models.game_session import GameSession

from app.models.song import Song

# schemas
from app.schemas.game import StartGameRequest, SubmitGameRequest

# websocket
from app.ws.session import sessions

# services
from app.services.song import get_random_song

from app.services.statistics import update_statistics

from app.services.leaderboard import update_leaderboard

# utils
from app.utils.constants import (
    MODE_AUDIO_CLIP_LENGTH,
    MODE_EXPIRES_IN,
    MODE_MAXIMUM_ATTEMPTS,
)

from app.utils.helpers import (
    calculate_time_in_minutes,
    get_time_until_end_of_day,
)

from app.api.v1.endpoints.enums import Result


# error
class NoSongAvailable(Exception):
    pass


class DailyGameNotFound(Exception):
    pass


class UserAlreadyPlayedDailyGame(Exception):
    pass


class InvalidNumberOfAttempts(Exception):
    pass


class SessionNotFound(Exception):
    pass


class DuplicateSession(Exception):
    pass


"""
Validators
"""


def assert_user_has_not_played_daily_game(db: Session, user_id: uuid.UUID):
    """
    Ensures the user has not already played today's daily game.

    Raises UserAlreadyPlayedDailyGame if the user has already played today.
    """

    # Obtain current date
    today = DateType.today()

    # Check for an existing daily game session for the user on the current date
    query = select(GameSession).where(
        GameSession.userID == user_id,
        GameSession.mode == "daily",
        GameSession.date == today,
    )

    already_played_daily_game = db.scalars(query).first()

    if already_played_daily_game:
        raise UserAlreadyPlayedDailyGame()


def assert_number_of_attempts_do_not_exceed_mode_maximum(mode: str, attempts: int):
    """
    Confirms the number of attempts does not exceed the game mode-specific maximum.

    Raises InvalidNumberOfAttempts if the given attempts exceed the allowed maximum for the mode.
    """

    # Get the allowed maximum attempts for the specified game mode
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

    if attempts > maximum_attempts:
        raise InvalidNumberOfAttempts()


def assert_game_session_is_unique(db: Session, ws_game_session_id: str):
    """
    Guarantees that the game session is not yet included in the database.

    Raises DuplicateSession if a WebSocket session with the given ID already exists.
    """
    # Query the database to check if the session ID already exists
    query = select(GameSession).where(GameSession.gameSessionID == ws_game_session_id)

    game_session_exists = db.scalars(query).first()

    if game_session_exists:
        raise DuplicateSession()


"""
Getters
"""


def get_daily_game(db: Session, date: DateType) -> DailyGame:
    """
    Retrieves the daily game configuration for a specific date.

    Raises DailyGameNotFound if no daily game exists for the given date.
    """

    query = select(DailyGame).where(DailyGame.date == date)

    daily_game = db.scalars(query).first()

    if not daily_game:
        raise DailyGameNotFound()

    return daily_game


def get_game_mode_start_at(mode: str, song_duration: int) -> int:
    """
    Determines a valid random starting position for a game mode's audio clip.
    """

    clip_length = MODE_AUDIO_CLIP_LENGTH[mode]

    # Ensure the clip does not exceed the song's duration
    maximum_start_at = max(0, song_duration - clip_length)

    return random.randint(0, maximum_start_at)


def get_game_mode_expires_in(mode: str) -> int:
    """
    Determines the session expiration time (in minutes) for a given game mode.
    """

    if mode == "daily":
        # Daily sessions expire at the end of the current day
        return calculate_time_in_minutes(get_time_until_end_of_day())
    else:
        # Non-daily modes use a predefined expiration duration
        return MODE_EXPIRES_IN[mode]


"""
Mains
"""


class StartGameResult:
    def __init__(
        self,
        *,
        song: Song,
        start_at: int,
        maximum_attempts: int,
        expires_in: int,
        date: Optional[DateType]
    ):
        self.song = song
        self.start_at = start_at
        self.maximum_attempts = maximum_attempts
        self.expires_in = expires_in
        self.date = date


def start_game_service(payload: StartGameRequest, db: Session) -> StartGameResult:
    """
    Resolves the game request into song, expiration and attempt rules.
    """

    # Decompose payload
    mode = payload.mode

    user_id = payload.userID

    date = payload.date

    # Resolve game data based on mode
    if mode in {"daily", "archive"}:
        # Determine which date the daily game should be loaded from
        date_input = date if (mode == "daily" and date) else DateType.today()

        # Retrieve the daily game configuration for the resolved date
        daily_game = get_daily_game(db, date_input)

        # Enforce daily-play restriction when applicable
        if mode == "daily" and user_id:
            assert_user_has_not_played_daily_game(db, user_id)

        song = daily_game.song

        start_at = daily_game.startAt

    else:
        # Fallback to random song selection for non-daily modes
        song = get_random_song(db)

        if not song:
            raise NoSongAvailable()

        # Randomize audio clip starting position based on mode
        start_at = get_game_mode_start_at(mode, song.duration)

        date = None

    # Resolve session constraints specific to mode
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

    expires_in = get_game_mode_expires_in(mode)

    return StartGameResult(
        song=song,
        start_at=start_at,
        maximum_attempts=maximum_attempts,
        expires_in=expires_in,
        date=date,
    )


def submit_game_service(payload: SubmitGameRequest, db: Session):
    """
    Handles the submission of a game session, validates it, and updates statistics and / or leaderboards if applicable.
    """

    # Decompose payload
    ws_game_session_id = payload.wsGameSessionID

    user_id = payload.userID

    mode = payload.mode

    won = payload.won

    attempts = payload.attempts

    date = payload.date

    # Validate submission

    # Check attempt count
    assert_number_of_attempts_do_not_exceed_mode_maximum(mode, attempts)

    # Get the WebSocket session from in-memory storage
    ws_game_session = sessions.get(ws_game_session_id)

    # Confirms that a WebSocket game session exists
    if not ws_game_session:
        raise SessionNotFound()

    # Ensure session has not already been submitted
    assert_game_session_is_unique(db, ws_game_session_id)

    # Enforce daily-play restriction when applicable
    if mode == "daily" and user_id:
        assert_user_has_not_played_daily_game(db, user_id)

    # Determine game result
    result = Result.win if won else Result.lose

    # Persist the game session in the database
    db_game_session = GameSession(
        wsGameSessionID=ws_game_session_id,
        userID=user_id,
        mode=mode,
        result=result,
        songID=ws_game_session.answer_song_id,
        date=date,
    )

    db.add(db_game_session)

    # Update stats and leaderboard if the user is logged in
    if user_id:
        update_statistics(db=db, payload=payload)

        update_leaderboard(db=db, payload=payload)
