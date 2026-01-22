# standard library
from datetime import datetime, timezone

# FastAPI
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# app core
from app.db.get_db import db_session

# schemas
from pydantic import ValidationError

from app.schemas.game import ClientGuess

# services
from app.services.song import get_song_metadata_by_songID

# websocket
from app.ws.connection_manager import manager

from app.ws.session import sessions

from app.ws.session_manager import check_guess


router = APIRouter()


@router.websocket("/{game_session_id}")
async def game_ws(websocket: WebSocket, game_session_id: str):
    # Get the session
    session = sessions.get(game_session_id)

    # Check if session exists
    if not session:
        # Accept the WebSocket connection to send an error message
        await websocket.accept()

        # Send the error message
        await websocket.send_json({"error": "Invalid session."})

        # Close Websocket connection
        await websocket.close()

        return

    await manager.connect(game_session_id, websocket)

    try:
        while True:
            # Validate expiration of the game session
            if session.expires_at < datetime.now(timezone.utc):
                # Notify the client about expiration
                await manager.send(game_session_id, {"type": "expired"})

                # Break the game loop
                break

            # Wait for a guess

            # {
            #   "type":  "guess",
            #   "guess": string,
            # }
            data = await websocket.receive_json()

            # Validate message format
            try:
                message = ClientGuess.model_validate(data)

            except ValidationError:
                await manager.send(game_session_id, {"error": "Invalid client message format."})

                continue

            # Process the guess

            # {
            #   "type":       "result",
            #   "is_correct": bool,
            #   "done":       bool,
            #   "guess":      str,
            #   "attempts":   int,
            # }
            response = check_guess(game_session_id, message.guess)

            # Send back the response
            await manager.send(game_session_id, response.model_dump())

            # Break the game loop if the game is finished
            if response.done == True:
                # Fetch song metadata
                with db_session() as db:
                    song_metadata = get_song_metadata_by_songID(
                        db,
                        session.answer_song_id
                    )

                # Send metadata for the end game pop up
                await manager.send(game_session_id, song_metadata.model_dump(mode="json"))

                break

    except WebSocketDisconnect:
        pass

    finally:
        # Clean up on disconnect
        await manager.disconnect(game_session_id)

        # Remove the session from active sessions
        sessions.pop(game_session_id, None)