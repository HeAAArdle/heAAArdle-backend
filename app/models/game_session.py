from sqlalchemy import Date, ForeignKey, ForeignKeyConstraint

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from datetime import date as DateType

from app.db.base import Base

from app.models.daily_game import DailyGame
from app.models.enums import modes, results

class GameSession(Base):
    __tablename__ = "game_sessions"

    gameSessionID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    wsGameSessionID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True, unique=True
    )

    mode:   Mapped[str] = mapped_column(modes, nullable=False, index=True)
    result: Mapped[str] = mapped_column(results, nullable=False, index=True)

    # Foreign Keys

    userID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.userID"), nullable=False, index=True
    )
    songID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    date: Mapped[DateType] = mapped_column(Date, nullable=True, index=True)

    # Relationships

    # GameSession <-> User: Many-to-One
    user: Mapped["User"] = relationship(
        "User", back_populates="game_sessions"
    )

    # GameSession <-> DailyGame: Many-to-One
    daily_game: Mapped["DailyGame"] = relationship(
        "DailyGame", back_populates="game_sessions"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["songID", "date"],
            ["daily_games.songID", "daily_games.date"]
        ),
    )