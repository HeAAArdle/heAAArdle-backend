# standard library
import uuid

from datetime import date as DateType

# SQLAlchemy
from sqlalchemy import select

from sqlalchemy.orm import Session

# models
from app.models import *

# exceptions
from app.services.exceptions import (
    DuplicateSession,
    InvalidNumberOfAttempts,
    UserAlreadyThePlayedDailyGame,
)

# utils
from app.utils.constants import MODE_MAXIMUM_ATTEMPTS


def assert_user_has_not_played_the_daily_game(db: Session, user_id: uuid.UUID):
    """
    Verify that the user has not played today's daily game.

    Raises:
        UserAlreadyThePlayedDailyGame: If the user has already played today.
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
        raise UserAlreadyThePlayedDailyGame()


def assert_number_of_attempts_do_not_exceed_the_mode_maximum(mode: str, attempts: int):
    """
    Ensure the number of attempts does not exceed the allowed maximum for the game mode.

    Raises:
        InvalidNumberOfAttempts: If attempts exceed the mode-specific maximum.
    """

    # Retrieve the maximum allowed attempts for the specified mode
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

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
