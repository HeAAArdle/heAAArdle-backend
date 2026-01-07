from sqlalchemy import Column, Table, ForeignKey

from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

song_is_by_artist = Table(
    "song_artist",
    Base.metadata,
    Column("songID", UUID(as_uuid=True), ForeignKey("songs.songID"), primary_key=True),
    Column("artistID", UUID(as_uuid=True), ForeignKey("artists.artistID"), primary_key=True),
)