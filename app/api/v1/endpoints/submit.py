# FastAPI
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# schemas
from app.schemas.game import SubmitGameRequest

# services
from app.services.game import (
    InvalidNumberOfAttempts,
    SessionNotFound,
    DuplicateSession,
    UserAlreadyPlayedDailyGame,
    submit_game_service,
)


router = APIRouter()


@router.post("/submit")
def submit_game(payload: SubmitGameRequest, db: Session = Depends(get_db)):
    try:
        # Process the submitted game and persist results
        submit_game_service(payload, db)

    except InvalidNumberOfAttempts:
        raise HTTPException(400, "Invalid number of attempts for the game mode.")

    except SessionNotFound:
        raise HTTPException(404, "Game session not found.")

    except DuplicateSession:
        raise HTTPException(409, "Result already submitted for this session.")

    except UserAlreadyPlayedDailyGame:
        raise HTTPException(403, "User has already played today's daily game.")

    # No response body needed for successful submission
    return None
