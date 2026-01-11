# SQLAlchemy
from sqlalchemy.orm import Session

from sqlalchemy import select, func

# models
from app.models.song import Song


def get_all_song_titles(db: Session) -> list[str]:
    """
    Gets an alphabetically-ordered list containing the titles of all songs in the database.
    """

    query = select(Song.title).order_by(Song.title)

    song_list = db.scalars(query).all()

    return [row[0] for row in song_list]


def get_random_song(db: Session) -> Song | None:
    """
    Fetches a random song.
    """

    query = select(Song).order_by(func.random())

    song = db.scalars(query).first()

    return song
