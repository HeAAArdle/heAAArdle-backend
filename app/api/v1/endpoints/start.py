# FastAPI
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select, func

from sqlalchemy.orm import Session

# app core
from app.core.config import settings

from app.db.get_db import get_db

# models
from app.models.daily_game import DailyGame

from app.models.game_session import GameSession

from app.models.song import Song

# schemas
from app.schemas.game import StartGameRequest, StartGameResponse

# websocket
from app.ws.session import sessions, GameSession as WSGameSession

# standard library
import random

from datetime import date

# utils
from app.utils.helpers import (
    calculate_time_in_minutes,
    get_time_until_end_of_day,
    generate_unique_game_session_id,
)

from app.utils.constants import (
    MODE_AUDIO_CLIP_LENGTH,
    MODE_EXPIRES_IN,
    MODE_MAXIMUM_ATTEMPTS,
)


router = APIRouter()


@router.post("/start", response_model=StartGameResponse)
def start_game(payload: StartGameRequest, db: Session = Depends(get_db)):
    # Decompose payload
    mode = payload.mode

    user_id = payload.userID

    if mode == "daily":
        # Extract current date
        today = date.today()  # In format YYYY-MM-DD

        # Fetch the daily game for the current date
        query1 = select(DailyGame).where(DailyGame.date == today)

        daily_game = db.scalars(query1).first()

        # Validate daily game existence
        if not daily_game:
            raise HTTPException(
                status_code=404, detail="No song available for today's daily Heardle."
            )

        # Implementation may change: Verify userID if provided (e.g., check if the user has already played today's daily game)
        if user_id:
            query2 = select(GameSession).where(
                GameSession.userID == user_id,
                GameSession.mode == "daily",
                GameSession.date == today,
            )

            user_already_played_daily_game = db.scalars(query2).first()

            if user_already_played_daily_game:
                raise HTTPException(
                    status_code=403,
                    detail="User has already played today's daily Heardle.",
                )

        song = daily_game.song

        start_at = daily_game.startAt

        # Set expiration time until the end of the day as per system design
        expires_in = calculate_time_in_minutes(get_time_until_end_of_day())

        game_date = today

    else:
        # For non-daily modes, select a random song from the database
        query3 = select(Song).order_by(func.random())

        song = db.scalars(query3).first()

        # Validate song existence
        if not song:
            raise HTTPException(status_code=500, detail="No songs available.")

        maximum_clip_length = MODE_AUDIO_CLIP_LENGTH[mode]

        # Calculate maximum possible start time to fit the audio clip within the song duration
        maximum_start_at = max(0, song.duration - maximum_clip_length)

        start_at = random.randint(0, maximum_start_at)

        expires_in = MODE_EXPIRES_IN[mode]

        game_date = None

    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

    # Generate a unique WebSocket game session ID
    game_session_id = generate_unique_game_session_id(sessions)

    # Create a new WebSocket game session
    sessions[game_session_id] = WSGameSession(
        answer=song.title,
        answer_song_id=song.songID,
        user_id=user_id,
        mode=mode,
        date=game_date,
        maximum_attempts=maximum_attempts,
        expires_in=expires_in,
    )

    return StartGameResponse(
        wsGameSessionID=game_session_id,
        expiresIn=expires_in,
        wsURL=f"wss://{settings.host}/api/v1/ws/game/{game_session_id}",
        audio=song.audio,
        startAt=start_at,
        date=game_date,
    )
