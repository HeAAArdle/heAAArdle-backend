from sqlalchemy import Integer, String, Text

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

from app.models.song__artist import SongArtist

class Song(Base):
    __tablename__ = "songs"

    songID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    title:       Mapped[str] = mapped_column(String, nullable=False, index=True)
    releaseYear: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    album:       Mapped[str] = mapped_column(String, nullable=True, index=True)
    shareLink:   Mapped[str] = mapped_column(String, unique=True, nullable=False)
    audioLink:   Mapped[str] = mapped_column(String, unique=True, nullable=False)
    lyrics:      Mapped[str] = mapped_column(Text, nullable=False) # long text; no index because of size
    duration:    Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Relationships

    # Song <-> Artist: Many-to-Many
    song_artists: Mapped[list["SongArtist"]] = relationship(
        back_populates="song"
    )

    # Song <-> DailyGame: One-to-Many
    daily_games: Mapped[list["DailyGame"]]  = relationship(
        "DailyGame", back_populates="song"
    )
