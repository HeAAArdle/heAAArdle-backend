# FastAPI
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select

from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# models
from app.models.game_session import GameSession as DBGameSession

# schemas
from app.schemas.game import SubmitGameRequest

# websocket
from app.ws.session import sessions

# services
from app.services.leaderboard import update_leaderboard

from app.services.statistics import update_statistics

# utils
from app.api.v1.endpoints.enums import Result

from app.utils.constants import MODE_MAXIMUM_ATTEMPTS

router = APIRouter()


@router.post("/submit")
def submit_game(payload: SubmitGameRequest, db: Session = Depends(get_db)):
    # Decompose payload
    ws_game_session_id = payload.wsGameSessionID
    user_id = payload.userID
    mode = payload.mode
    won = payload.won
    attempts = payload.attempts
    date = payload.date

    # Validate attempt count
    maximum_attempts = MODE_MAXIMUM_ATTEMPTS[mode]

    # If attempts is greater than the maximum attempts for the mode, error
    if attempts > maximum_attempts:
        raise HTTPException(
            status_code=400, detail="Invalid attempts for the Game Mode."
        )

    # Validate uniqueness of result
    query = select(DBGameSession).where(
        DBGameSession.gameSessionID == ws_game_session_id
    )

    game_session_data_exists = db.scalars(query).first()

    if game_session_data_exists:
        raise HTTPException(
            status_code=409, detail="Result is already submitted for this session."
        )

    # Fetch the WebSocket session to get the song ID
    ws_game_session = sessions.get(ws_game_session_id)

    if not ws_game_session:
        raise HTTPException(status_code=404, detail="Game session not found.")

    # Determine result based on whether the player won or lost
    result = Result.win if won else Result.lose

    # Store the game session in the database
    db_game_session = DBGameSession(
        wsGameSessionID=ws_game_session_id,
        userID=user_id,
        mode=mode,
        result=result,
        songID=ws_game_session.answer_song_id,
        date=date,
    )

    db.add(db_game_session)

    # Implementation may change: Update Statistics and / or Leaderboard if the user is logged in
    if user_id:
        update_statistics(db=db, payload=payload)

        update_leaderboard(db=db, payload=payload)

    db.commit()

    return None
