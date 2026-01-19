# standard library
import uuid

from datetime import date as DateType, datetime, timedelta, timezone

from dataclasses import dataclass, field

from typing import Optional

# schemas
from app.schemas.enums import GameMode


@dataclass
class GameSession:
    answer: str
    answer_song_id: uuid.UUID

    user_id: Optional[uuid.UUID]

    mode: GameMode
    date: Optional[DateType]

    maximum_attempts: int

    expires_in_minutes: int

    attempts: int = field(default=0, init=False)
    done: bool = field(default=False, init=False)

    created_at: datetime = field(init=False)
    expires_at: datetime = field(init=False)

    def __post_init__(self):
        # Normalize answer
        self.answer = self.answer.lower()

        # Timestamps
        self.created_at = datetime.now(timezone.utc)
        self.expires_at = self.created_at + timedelta(minutes=self.expires_in_minutes)


sessions: dict[str, GameSession] = {}  # { key: gameSessionID, value: GameSession }
