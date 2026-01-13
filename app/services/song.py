# SQLAlchemy
from sqlalchemy.orm import Session

from sqlalchemy import select, func

# app core
from app.db.supabase import supabase

# models
from app.models import *

# schemas
from app.schemas.enums import GameMode

# services
from app.services.game.game_domain import get_expires_in_minutes_by_game_mode

# exceptions
from app.services.exceptions import NoSongAvailable

# utils
from app.utils.helpers import calculate_minutes_to_seconds


def get_all_song_titles(db: Session) -> list[str]:
    """
    Retrieve an alphabetically ordered list of all song titles.

    Returns:
        A list of song titles sorted in ascending order.
    """

    # Query only song titles and sort them alphabetically
    query = select(Song.title).order_by(Song.title)

    song_titles = db.scalars(query).all()

    # Extract titles from the query result
    return [title for title in song_titles]


def get_random_song(db: Session) -> Song:
    """
    Retrieve a single song selected at random from the database.

    Returns:
        A randomly selected Song.

    Raises:
        NoSongAvailable: If the database contains no songs.
    """

    # Randomize song order and select the first result
    query = select(Song).order_by(func.random())

    song = db.scalars(query).first()

    if not song:
        raise NoSongAvailable()

    return song


def get_signed_audio_link(mode: GameMode, audio_link: str) -> str:
    """
    Generate a time-limited signed URL for a song’s audio file based on the selected game mode.

    The URL expires according to the mode-specific session duration.

    Returns:
        A signed URL that allows temporary access to the audio file.
    """

    # Determine the expiration duration based on game mode
    expires_in_minutes = get_expires_in_minutes_by_game_mode(mode)

    # Convert expiration duration to seconds
    expires_in_seconds = calculate_minutes_to_seconds(expires_in_minutes)

    # Create a signed URL for the audio file in the buckets
    link = supabase.storage.from_("songs").create_signed_url(
        audio_link,
        expires_in_seconds,
    )

    return link["signedUrl"]
