from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.db.get_db import get_db

from app.models.game_session import GameSession as DBGameSession

from app.schemas.game import SubmitGameRequest

from app.ws.session import GameSession as WSGameSession

from app.services.constants import MODE_MAXIMUM_ATTEMPTS

from app.services.statistics import update_statistics

from app.services.leaderboard import update_leaderboard

router = APIRouter()

@router.post("/submit")
def submit_game(payload: SubmitGameRequest, db: Session = Depends(get_db)):
    mode = payload.mode

    # Validate date based on mode

    # If mode is Daily, a date must be provided
    if mode == "daily" and payload.date is None:
        raise HTTPException(status_code=400, detail="Daily Mode requires a date.")

    # If mode is Original, a date must not be provided
    if mode == "original" and payload.date is not None:
        raise HTTPException(
            status_code=400, detail="Original Mode must not have a date."
        )

    # Validate attempt count
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[payload.mode]

    # If attempts is less than 1 or greater than the maximum attempts for the mode, error
    if payload.attempts < 1 or payload.attempts > maximum_attempts:
        raise HTTPException(
            status_code=400, detail="Invalid attempts for the Game Mode."
        )

    # Validate uniqueness of result
    game_session_data_exists = (
        db.query(DBGameSession)
        .filter(DBGameSession.gameSessionID == payload.gameSessionID)
        .first()
    )

    if game_session_data_exists:
        raise HTTPException(
            status_code=409, detail="Result is already submitted for this session."
        )

    # Fetch the WebSocket session to get the song ID
    ws_game_session = WSGameSession.get(payload.gameSessionID)

    if not ws_game_session:
        raise HTTPException(status_code=404, detail="Game session not found.")

    # Determine result based on whether the player won or lost
    result = "win" if payload.won else "lose"

    # Store the game session in the database
    db_game_session = DBGameSession(
        gameSessionID=payload.gameSessionID,
        userID=payload.userID,
        mode=payload.mode,
        result=result,
        songID=ws_game_session.songID,
        date=payload.date,
    )

    db.add(db_game_session)

    # Update Statistics and / or Leaderboard if the user is logged in
    if payload.userID:
        update_statistics(db=db, payload=payload)
        update_leaderboard(db=db, payload=payload)

    db.commit()

    return None
