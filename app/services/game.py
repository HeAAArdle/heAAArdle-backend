from app.ws.session import sessions


def process_guess(game_session_id: str, guess: str) -> dict[str, str | bool]:
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
