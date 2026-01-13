from sqlalchemy import Date, ForeignKey

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

from app.models.song import Song

class DailyGame(Base):
    __tablename__ = "daily_games"

    date: Mapped[Date] = mapped_column(Date, primary_key=True)

    # Foreign Keys

    songID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.songID"), primary_key=True
    )

    # Relationships

    # DailyGame <-> Song: Many-to-One
    song: Mapped["Song"] = relationship( # type: ignore
        "Song", back_populates="daily_games"
    )

    # DailyGame <-> GameSession: One-to-Many
    game_sessions: Mapped[list["GameSession"]] = relationship( # type: ignore
        "GameSession", back_populates="daily_game"
    )

# (songID, date) is the composite primary key