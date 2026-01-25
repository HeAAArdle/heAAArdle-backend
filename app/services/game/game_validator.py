# standard library
import uuid

from datetime import date as DateType

# SQLAlchemy
from sqlalchemy import select

from sqlalchemy.orm import Session

# models
from app.models import *

# schemas
from app.schemas.enums import GameMode

# exceptions
from app.services.exceptions import (
    DateProvided,
    DateIsTodayOrInTheFuture,
    DuplicateSession,
    InvalidNumberOfAttempts,
    UserAlreadyPlayedTheDailyGame,
)

# services
from app.services.game.game_domain import get_maximum_attempts_by_game_mode

from app.services.song import get_song_by_songID


def assert_date_is_not_today_or_in_the_future(date: DateType):
    """
    Ensure that the given date is not today or in the future.

    Raises:
        DateIsTodayOrInTheFuture: If the date is later than yesterday.
    """

    # Get today's date
    today = DateType.today()

    # Check if the given date occurs on the same day or after the current date
    if date >= today:
        raise DateIsTodayOrInTheFuture()


def assert_date_is_valid_for_non_archive_mode(date: DateType | None):
    """
    Ensure that no date is provided for non-archive game modes.

    Raises:
        DateProvided: If a date is supplied for a game mode that does not accept dates.
    """

    # Disallow explicit date input for non-archive modes
    if date is not None:
        raise DateProvided()


def assert_user_has_not_played_the_daily_game(db: Session, user_id: uuid.UUID):
    """
    Verify that the user has not played today's daily game.

    Raises:
        UserAlreadyPlayedTheDailyGame: If the user has already played today.
    """

    # Get today's date
    today = DateType.today()

    # Check if a daily game session exists for this user today
    query = select(GameSession).where(
        GameSession.userID == user_id,
        GameSession.mode == GameMode.DAILY,
        GameSession.date == today,
    )

    if db.scalars(query).first():
        raise UserAlreadyPlayedTheDailyGame()


def assert_number_of_attempts_do_not_exceed_the_mode_maximum(
    mode: GameMode, attempts: int
):
    """
    Ensure the number of attempts does not exceed the allowed maximum for the game mode.

    Raises:
        InvalidNumberOfAttempts: If attempts exceed the mode-specific maximum.
    """

    # Retrieve the maximum allowed attempts for the specified mode
    maximum_attempts = get_maximum_attempts_by_game_mode(mode)

    if attempts > maximum_attempts:
        raise InvalidNumberOfAttempts()


def assert_song_exists(db: Session, song_id: uuid.UUID):
    """
    Ensure the song the frontend passes exists in the database.

    Raises:
        SongNotFound: If the given song is not in the database.
    """

    get_song_by_songID(db, song_id)


def assert_game_session_is_unique(db: Session, ws_game_session_id: str):
    """
    Ensure the WebSocket game session ID is not already in the database.

    Raises:
        DuplicateSession: If a session with the given ID already exists.
    """

    # Check for an existing game session with the same WebSocket ID
    query = select(GameSession).where(GameSession.wsGameSessionID == ws_game_session_id)

    if db.scalars(query).first():
        raise DuplicateSession()
