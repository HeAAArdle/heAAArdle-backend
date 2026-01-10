from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import func

from sqlalchemy.orm import Session

from app.core.config import settings

from app.db.get_db import get_db

from app.models.daily_game import DailyGame

from app.models.game_session import GameSession

from app.models.song import Song

from app.schemas.game import StartGameRequest, StartGameResponse

from datetime import date

import random

import uuid

from app.ws.session import sessions, GameSession as WSGameSession

from app.utils.helpers import get_time_until_end_of_day, calculate_time_in_minutes

router = APIRouter()

MODE_AUDIO_CLIP_LENGTH = {
    "original": 16,
    "daily":    16,
    "rapid":    3,
}

MODE_MAXIMUM_ATTEMPTS = {
    "original": 6,
    "daily":    6,
    "rapid":    1,
    "lyrics":   1,
}

MODE_EXPIRES_AT = {
    "original": 15,
    "rapid"   : 2,
    "lyrics"  : 2,
}

@router.post("/start", response_model=StartGameResponse)
def start_game(payload: StartGameRequest, db: Session = Depends(get_db)):
    mode = payload.mode

    if mode == "daily":
        # Extract current date
        today = date.today() # In format YYYY-MM-DD

        # Fetch the daily game for the current date
        daily_game = db.query(DailyGame).filter(DailyGame.date == today).first()

        # Validate daily game existence
        if not daily_game:
            raise HTTPException(status_code=404, detail="No song available for today's daily game.")
        
        # Implementation may change: Verify userID if provided (e.g., check if the user has already played today's daily game)
        if payload.userID:
            user_already_played_daily_game = db.query(GameSession).filter(
                GameSession.userID == payload.userID,
                GameSession.date == today,
                GameSession.mode == "daily"
            ).first()

            if user_already_played_daily_game:
                raise HTTPException(status_code=403, detail="User has already played today's daily game.")
        
        song = daily_game.song

        start_at = daily_game.startAt

        # Set expiration time until the end of the day as per system design
        expires_in = calculate_time_in_minutes(get_time_until_end_of_day())

        game_date = today     

    else:
        # For non-daily modes, select a random song from the database
        song = db.query(Song).order_by(func.random()).first()
    
        # Validate song existence
        if not song:
            raise HTTPException(status_code=500, detail="No songs available in the database.")

        maximum_clip_length = MODE_AUDIO_CLIP_LENGTH[mode]

        # Calculate maximum possible start time to fit the audio clip within the song duration
        maximum_start_at = max(0, song.duration - maximum_clip_length)

        start_at = random.randint(0, maximum_start_at)

        expires_in = MODE_EXPIRES_AT[mode]

        game_date = None

    # Set mode-specific parameters
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

    # Create a new game session

    # Generate a unique game session ID
    game_session_id = str(uuid.uuid4())

    sessions[game_session_id] = WSGameSession(
        answer=song.title,
        user_id=payload.userID,
        mode=mode,
        date=game_date,
        maximum_attempts=maximum_attempts,
        expires_in=expires_in
    )

    return StartGameResponse(
        gameSessionID=game_session_id,
        expiresIn=expires_in,
        wsURL=f"wss://{settings.host}/api/v1/ws/game/{game_session_id}",
        audio=song.audio,
        startAt=start_at,
        date=game_date
    )