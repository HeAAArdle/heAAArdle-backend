from sqlalchemy import Column, String

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

import uuid

from app.db.base import Base

class Artist(Base):
    __tablename__ = "artists"

    artistID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, index=True, nullable=False)

    # Relationships

    songs = relationship("Song", secondary="song_is_by_artist", back_populates="artists")