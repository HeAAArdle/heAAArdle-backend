from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.artist import Artist
    from app.models.song import Song

class SongArtist(Base):
    __tablename__ = "song__artist"

    songID:   Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.songID"), primary_key=True
    )
    artistID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artists.artistID"), primary_key=True
    )

    # Relationships

    song: Mapped["Song"] = relationship(
        back_populates="song_artists"
    )

    artist: Mapped["Artist"] = relationship(
        back_populates="song_artists"
    )