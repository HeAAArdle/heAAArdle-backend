# standard library
from datetime import date
from typing import Optional
import uuid

# websocket
from app.ws.session import sessions, GameSession


def create_unique_ws_game_session_id(sessions: dict[str, GameSession]) -> str:
    """
    Generates a unique WebSocket game session ID.

    Returns a UUID string that does not collide with existing game session IDs.
    """

    # Generate IDs until a non-colliding one is found
    while True:
        session_id = str(uuid.uuid4())

        if session_id not in sessions:
            return session_id


def create_ws_game_session(
    answer: str,
    answer_song_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    mode: str,
    date: Optional[date],
    maximum_attempts: int,
    expires_in: int,
) -> str:
    """
    Makes and stores an in-memory WebSocket game session.

    Returns the ID of the created WebSocket game session.
    """

    # Generate a unique identifier for the new WebSocket session
    game_session_id = create_unique_ws_game_session_id(sessions)

    # Persist the session state in memory for active WebSocket connections
    sessions[game_session_id] = GameSession(
        answer=answer,
        answer_song_id=answer_song_id,
        user_id=user_id,
        mode=mode,
        date=date,
        maximum_attempts=maximum_attempts,
        expires_in=expires_in,
    )

    return game_session_id


def check_guess(game_session_id: str, guess: str) -> dict[str, str | bool]:
    """
    Validates a user's guess.

    Returns a dictionary containing a boolean value indicating whether the
    game is over and whether the user guessed the answer correctly.
    """
    # Retrieve the session
    session = sessions[game_session_id]

    # If the session is already done, return done response immediately
    if session.done == True:
        return {"type": "result", "is_correct": False, "done": True}

    # Update attempts count
    session.attempts += 1

    # Check if the guess is correct by comparing normalized strings of the guess and the answer (titles)
    is_correct = guess.lower().strip() == session.answer.lower().strip()

    # Determine if the game is done
    if is_correct or session.attempts >= session.maximum_attempts:
        done = True

        # Mark the session as done
        session.done = True
    else:
        done = False

    # Prepare the response
    return {"type": "result", "is_correct": is_correct, "done": done}
