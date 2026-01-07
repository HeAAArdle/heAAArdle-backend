from sqlalchemy import Column, Date, ForeignKey

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

class DailyGame(Base):
    __tablename__ = "daily_games"

    date = Column(Date, primary_key=True)

    # Foreign Keys

    songID = Column(UUID(as_uuid=True), ForeignKey("songs.songID"), primary_key=True)

    # Relationships

    song = relationship("Song", back_populates="daily_games")

    game_sessions = relationship("GameSession", back_populates="daily_game")

# (songID, date) the composite primary key