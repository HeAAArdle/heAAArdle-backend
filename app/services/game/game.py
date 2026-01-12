# standard library
import uuid

from datetime import date as DateType

from typing import Optional

# SQLAlchemy
from sqlalchemy.orm import Session

# models
from app.models import *

# schemas
from app.schemas.game import StartGameRequest, SubmitGameRequest

# websocket
from app.ws.session import sessions

# services
from app.services.game.game_domain import (
    get_daily_game,
    get_expires_in_by_game_mode,
    get_start_at_by_game_mode,
)

from app.services.game.game_validator import (
    assert_game_session_is_unique,
    assert_number_of_attempts_do_not_exceed_the_mode_maximum,
    assert_user_has_not_played_the_daily_game,
)

from app.services.song import get_random_song

from app.services.statistics import update_statistics

from app.services.leaderboard import update_leaderboard

# exceptions
from app.services.exceptions import (
    NoSongAvailable,
    SessionNotFound,
)

# utils
from app.utils.constants import MODE_MAXIMUM_ATTEMPTS

from app.api.v1.endpoints.enums import Result


class StartGameDTO:
    def __init__(
        self,
        *,
        song: Song,
        start_at: Optional[int],
        maximum_attempts: int,
        expires_in: int,
        date: Optional[DateType]
    ):
        self.song = song
        self.start_at = start_at
        self.maximum_attempts = maximum_attempts
        self.expires_in = expires_in
        self.date = date


def start_game_service(
    payload: StartGameRequest, db: Session, user_id: Optional[uuid.UUID]
) -> StartGameDTO:
    """
    Resolve a start-game request into the song, timing, and rule constraints
    for the selected game mode.
    """

    # Decompose payload
    mode = payload.mode

    date = payload.date

    ##

    # Resolution

    if mode in {"daily", "archive"}:
        # Determine which date the daily game should be loaded from
        date_input = date if (mode == "daily" and date) else DateType.today()

        # Obtain the daily game configuration for the resolved date
        daily_game = get_daily_game(db, date_input)

        song = daily_game.song

        start_at = daily_game.startAt

        date = date_input

    else:
        # Use a randomly selected song for non-daily modes
        song = get_random_song(db)

        if not song:
            raise NoSongAvailable()

        start_at, date = None, None

    # Compute a clip starting position for non-lyrics modes
    if mode != "lyrics":
        start_at = get_start_at_by_game_mode(mode, song.duration)

    # Resolve constraints
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

    expires_in = get_expires_in_by_game_mode(mode)

    ##

    # Validation

    # Enforce daily-play restriction for authenticated users
    if mode == "daily" and user_id:
        assert_user_has_not_played_the_daily_game(db, user_id)

    # Construct and return the start-game response
    return StartGameDTO(
        song=song,
        start_at=start_at,
        maximum_attempts=maximum_attempts,
        expires_in=expires_in,
        date=date,
    )


def submit_game_service(payload: SubmitGameRequest, db: Session, user_id: uuid.UUID):
    """
    Validate and persist a completed game session,
    updating user statistics and leaderboards when applicable.
    """

    # Decompose payload
    ws_game_session_id = payload.wsGameSessionID

    mode = payload.mode

    date = payload.date

    won = payload.won

    attempts = payload.attempts

    ##

    # Validation

    # Validate attempt count
    assert_number_of_attempts_do_not_exceed_the_mode_maximum(mode, attempts)

    # Get the WebSocket session from in-memory storage
    ws_game_session = sessions.get(ws_game_session_id)

    # Confirm that a WebSocket game session exists
    if not ws_game_session:
        raise SessionNotFound()

    # Prevent duplicate submissions
    assert_game_session_is_unique(db, ws_game_session_id)

    # Enforce daily-play restriction for authenticated users
    if mode == "daily" and user_id:
        assert_user_has_not_played_the_daily_game(db, user_id)

    ##

    # Persistence

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

    ##

    # Side-effects

    # Update stats and leaderboard if the user is logged in
    if user_id:
        update_statistics(payload, db, user_id)

        update_leaderboard(payload, db, user_id)
