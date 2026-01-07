from sqlalchemy import Column, Date, ForeignKey, ForeignKeyConstraint

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import UUID

import uuid

from enums import results

from app.db.base import Base

class GameSession(Base):
    __tablename__ = "game_sessions"

    gameSessionID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    result: Mapped[str] = mapped_column(results, index=True, nullable=False)

    # Foreign Keys

    userID = Column(UUID(as_uuid=True), ForeignKey("users.userID"), index=True, nullable=False)
    songID = Column(UUID(as_uuid=True), ForeignKey("songs.songID"), index=True, nullable=True)
    date   = Column(Date, ForeignKey("daily_games.date"), index=True, nullable=True)

    # Relationships

    user = relationship("User", back_populates="game_sessions")
    daily_games = relationship("DailyGame", back_populates="game_sessions")

    __table_args__ = (
        ForeignKeyConstraint(
            ["songID", "date"],
            ["daily_games.songID", "daily_games.date"]
        ),
    )