from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

import uuid

from app.db.base import Base

class Song(Base):
    __tablename__ = "songs"

    songID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title       = Column(String, index=True, nullable=False)
    releaseYear = Column(Integer, index=True, nullable=False)
    album       = Column(String, index=True, nullable=True)
    link        = Column(String, unique=True, index=True, nullable=False)
    audio       = Column(String, unique=True, index=True, nullable=False)
    lyrics      = Column(String, nullable=False) # long text, no index because of size

    # Relationships

    artists = relationship("Artist", secondary="song_is_by_artist", back_populates="songs")
    daily_games = relationship("DailyGame", back_populates="song")