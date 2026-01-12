# standard library
from datetime import date as DateType

from typing import Optional

import uuid

# websocket
from app.ws.session import sessions, GameSession


def create_ws_game_session_id(sessions: dict[str, GameSession]) -> str:
    """
    Generate a unique WebSocket game session ID.

    Returns:
        A UUID string that does not collide with existing session IDs.
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
    date: Optional[DateType],
    maximum_attempts: int,
    expires_in: int,
) -> str:
    """
    Make and store an in-memory WebSocket game session.

    Returns:
        The ID of the created WebSocket game session.
    """

    # Generate a unique identifier for the WebSocket session
    game_session_id = create_ws_game_session_id(sessions)

    # Store the session state for active WebSocket connections
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
    Validate a user's guess against the active WebSocket game session.

    Returns:
        A result payload indicating whether the guess is
        correct and whether the game session is complete.
    """

    # Retrieve the active game session
    session = sessions[game_session_id]

    # Immediately return if the session has already ended
    if session.done == True:
        return {"type": "result", "is_correct": False, "done": True}

    # Increment the number of attempts for this session
    session.attempts += 1

    # Check if the guess is correct by comparing normalized strings of the guess and the answer
    is_correct = guess.lower() == session.answer

    # Determine whether the game should end
    if is_correct or session.attempts >= session.maximum_attempts:
        done = True

        # Mark the session as completed
        session.done = True
    else:
        done = False

    # Return the result of the guess
    return {"type": "result", "is_correct": is_correct, "done": done}
