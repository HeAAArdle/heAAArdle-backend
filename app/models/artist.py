from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

class Artist(Base):
    __tablename__ = "artists"

    artistID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Relationships

    # Artist <-> Song: Many-to-Many
    song_artists: Mapped[list["SongArtist"]] = relationship( # type: ignore
        back_populates="artist"
    )