# standard library
from typing import Optional

# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
from app.core.config import settings

from app.db.get_db import get_db

# models
from app.models.user import User

# schemas
from app.schemas.game import (
    AudioStartGameResponse,
    LyricsStartGameResponse,
    StartGameRequest,
    StartGameResponse,
)

from pydantic import AnyWebsocketUrl, HttpUrl

from app.schemas.enums import GameMode

# websocket
from app.ws.session_manager import create_ws_game_session

# services
from app.services.game.game import start_game_service

from app.services.song import get_signed_audio_link

from app.services.user.user_dependencies import get_optional_user

# exceptions
from app.services.exceptions import (
    AnswerPositionsLengthMismatch,
    ArchiveDateNotProvided,
    DateIsTodayOrInTheFuture,
    DateProvided,
    EmptyLyricsWords,
    NoSongAvailable,
    DailyGameNotFound,
    UserAlreadyPlayedTheDailyGame,
)

router = APIRouter()


@router.post("/start/", response_model=StartGameResponse)
def start_game(
    payload: StartGameRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    user_id = user.userID if user else None

    try:
        # Resolve game request
        result = start_game_service(payload, db, user_id)

    # Translate domain-specific errors into HTTP responses
    except DateProvided:
        raise HTTPException(400, "Non-archive modes should not have a date.")

    except NoSongAvailable:
        raise HTTPException(404, "No song available in the database.")

    except DailyGameNotFound:
        raise HTTPException(404, "No song available for the selected date.")

    except UserAlreadyPlayedTheDailyGame:
        raise HTTPException(403, "User has already played today's Heardle.")

    except EmptyLyricsWords:
        raise HTTPException(400, "No words available in lyrics.")

    except AnswerPositionsLengthMismatch:
        raise HTTPException(
            400, "Answer positions length does not match answer length."
        )

    except ArchiveDateNotProvided:
        raise HTTPException(400, "Archive mode requires a date.")

    except DateIsTodayOrInTheFuture:
        raise HTTPException(400, "Date cannot be in the future.")

    mode = payload.mode

    # Resolve the correct answer used for guess validation
    answer = (
        result.lyrics_answer if payload.mode == GameMode.LYRICS else result.song.title
    )

    if answer is None:
        raise HTTPException(500, "Game answer could not be resolved.")

    # Create a new WebSocket game session and return its ID
    ws_game_session_id = create_ws_game_session(
        answer,
        result.song.songID,
        user_id,
        mode,
        result.date,
        result.maximum_attempts,
        result.expires_in_minutes,
    )

    # Construct the WebSocket connection URL for the client

    scheme = "wss" if settings.env == "production" else "ws"

    ws_url = AnyWebsocketUrl(
        f"{scheme}://{settings.host}/{settings.websocket_endpoint_prefix}/{ws_game_session_id}"
    )

    expires_in_minutes = result.expires_in_minutes

    if mode == GameMode.LYRICS:
        # Lyrics mode requires pre-generated lyrics content
        if result.lyrics_given is None:
            raise HTTPException(
                500, "Lyrics game mode has no generated lyrics to display."
            )

        # Return the start response for lyrics-based gameplay
        return LyricsStartGameResponse(
            wsGameSessionID=ws_game_session_id,
            wsURL=ws_url,
            expiresInMinutes=expires_in_minutes,
            mode=mode,
            lyrics=result.lyrics_given,
            date=None,
        )

    else:
        # Audio-based modes require both a start time and audio source
        if result.audio_start_at is None or not result.song.audioLink:
            raise HTTPException(
                500, f"{mode} game mode has no audio or start time available."
            )

        # Generate a signed URL for more secure audio playback
        audio = HttpUrl(get_signed_audio_link(mode, result.song.audioLink))

        date = result.date

        # Return the start response for audio-based gameplay
        return AudioStartGameResponse(
            wsGameSessionID=ws_game_session_id,
            wsURL=ws_url,
            expiresInMinutes=expires_in_minutes,
            mode=mode,
            audio=audio,
            audioStartAt=result.audio_start_at,
            date=date,
        )
