from typing import Optional, Dict

from datetime import datetime, timedelta, timezone

class GameSession:
    def __init__(self, *, answer: str, user_id: Optional[str], mode: str, date: Optional[str], maximum_attempts: int, expires_in: int):
        self.answer = answer                     # the correct answer (song title)

        self.user_id = user_id

        self.mode = mode
        self.date = date                         # only for daily mode
        self.maximum_attempts = maximum_attempts

        self.attempts = 0
        self.done = False

        self.created_at = datetime.now(timezone.utc)
        
        self.expires_at = self.created_at + timedelta(minutes=expires_in)

sessions: Dict[str, GameSession] = {} # { key: gameSessionID, value: GameSession }