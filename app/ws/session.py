from typing import Optional

import uuid

from datetime import date, datetime, timedelta, timezone

class GameSession:
    def __init__(self, *, answer: str, answer_song_id: uuid.UUID, user_id: Optional[uuid.UUID], mode: str, date: Optional[date], maximum_attempts: int, expires_in: int):
        self.answer = answer.lower().strip() # correct answer (lowercase song title)
        self.answer_song_id = answer_song_id

        self.user_id = user_id

        self.mode = mode
        self.date = date
        self.maximum_attempts = maximum_attempts

        self.attempts = 0
        self.done = False

        self.created_at = datetime.now(timezone.utc)
        self.expires_at = self.created_at + timedelta(minutes=expires_in)

sessions: dict[str, GameSession] = {} # { key: gameSessionID, value: GameSession }
