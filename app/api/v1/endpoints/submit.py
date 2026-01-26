# FastAPI
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# models
from app.models.user import User

# schemas
from app.schemas.game import SubmitGameRequest

# services
from app.services.game.game import submit_game_service

from app.services.user.user_dependencies import get_current_user

# exceptions
from app.services.exceptions import (
    DatabasePersistenceFailed,
    InvalidNumberOfAttempts,
    DuplicateSession,
    SongNotFound,
    UserAlreadyPlayedTheDailyGame,
)

router = APIRouter()


@router.post("/submit/")
def submit_game(
    payload: SubmitGameRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user.userID

    try:
        # Process the submitted game and persist results
        submit_game_service(payload, db, user_id)

    except InvalidNumberOfAttempts:
        raise HTTPException(400, "Invalid number of attempts for the game mode.")

    except DuplicateSession:
        raise HTTPException(409, "Result already submitted for this session.")

    except UserAlreadyPlayedTheDailyGame:
        raise HTTPException(403, "User has already played today's Heardle.")

    except SongNotFound:
        raise HTTPException(404, "Song not found in the database.")

    except DatabasePersistenceFailed:
        raise HTTPException(500, "The database failed to persist the data.")

    return None
