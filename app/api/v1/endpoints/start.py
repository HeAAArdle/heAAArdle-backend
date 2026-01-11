# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
from app.core.config import settings

from app.db.get_db import get_db

# schemas
from app.schemas.game import StartGameRequest, StartGameResponse

# services
from app.services.game import (
    NoSongAvailable,
    DailyGameNotFound,
    UserAlreadyPlayedDailyGame,
    start_game_service,
)

from app.services.session import create_ws_game_session


router = APIRouter()


@router.post("/start", response_model=StartGameResponse)
def start_game(payload: StartGameRequest, db: Session = Depends(get_db)):
    try:
        # Resolve game request
        result = start_game_service(payload, db)

    except NoSongAvailable:
        raise HTTPException(404, "No song available.")

    except DailyGameNotFound:
        raise HTTPException(404, "No song available for the selected date.")

    except UserAlreadyPlayedDailyGame:
        raise HTTPException(403, "User has already played today's Heardle.")

    # Create a new WebSocket game session and return its ID
    game_session_id = create_ws_game_session(
        result.song.title,
        result.song.songID,
        payload.userID,
        payload.mode,
        result.game_date,
        result.maximum_attempts,
        result.expires_in,
    )

    # Return session metadata and playback configuration
    return StartGameResponse(
        wsGameSessionID=game_session_id,
        wsURL=f"wss://{settings.host}/{settings.websocket_endpoint_prefix}/{game_session_id}",
        expiresIn=result.expires_in,
        audio=result.song.audio,
        startAt=result.start_at,
        date=result.game_date,
    )
