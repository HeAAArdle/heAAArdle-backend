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
    DateIsInTheFuture,
    DuplicateSession,
    InvalidNumberOfAttempts,
    UserAlreadyPlayedTheDailyGame,
)

# services
from app.services.game.game_domain import get_maximum_attempts_by_game_mode


def assert_date_is_not_in_the_future(date: DateType, today: DateType):
    """
    Ensure that the provided date is not in the future.

    Raises:
        DateIsInTheFuture: If the date is later than today.
    """

    # Check if the given date occurs after the current date
    if date > today:
        raise DateIsInTheFuture()


def assert_date_is_not_given_for_non_archive_modes(date: DateType | None):
    """
    Ensure that no date is provided for modes that do not accept one.

    Raises:
        DateProvided: If a date is given for a non-daily or non-archive mode.
    """

    # Raise an error if a date is provided for a mode that does not accept it
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
        GameSession.mode == "daily",
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
