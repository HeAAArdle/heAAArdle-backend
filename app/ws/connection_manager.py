from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, game_session_id: str, websocket: WebSocket):
        await websocket.accept()

        self.connections[game_session_id] = websocket

    async def disconnect(self, game_session_id: str):
        ws = self.connections.get(game_session_id)

        if ws:
            await ws.close()

        self.connections.pop(game_session_id, None)

    async def send(self, game_session_id: str, message: dict[str, str | bool]):
        ws = self.connections.get(game_session_id)

        if ws:
            await ws.send_json(message)

manager = ConnectionManager()