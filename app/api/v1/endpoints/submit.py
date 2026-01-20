# standard library
import uuid

# FastAPI
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# schemas
from app.schemas.game import SubmitGameRequest, SubmitGameResponse

# services
from app.services.game.game import submit_game_service

# exceptions
from app.services.exceptions import (
    InvalidNumberOfAttempts,
    SessionNotFound,
    DuplicateSession,
    SongNotFound,
    UserAlreadyPlayedTheDailyGame,
)


router = APIRouter()


@router.post("/submit", response_model=SubmitGameResponse)
def submit_game(
    payload: SubmitGameRequest,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_optional_user),  # Uncomment once auth is available
):
    # Placeholder user ID until auth is available: current_user
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    # user_id = current_user.userID if current_user else None

    try:
        # Process the submitted game and persist results
        result = submit_game_service(payload, db, user_id)

    except InvalidNumberOfAttempts:
        raise HTTPException(400, "Invalid number of attempts for the game mode.")

    except SessionNotFound:
        raise HTTPException(404, "Game session not found.")

    except DuplicateSession:
        raise HTTPException(409, "Result already submitted for this session.")

    except UserAlreadyPlayedTheDailyGame:
        raise HTTPException(403, "User has already played today's Heardle.")

    except SongNotFound:
        raise HTTPException(404, "Song not found in the database.")

    # Return game result and song metadata
    return result
