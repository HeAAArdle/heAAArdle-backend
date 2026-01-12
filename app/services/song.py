# SQLAlchemy
from sqlalchemy.orm import Session

from sqlalchemy import select, func

# app core
from app.db.supabase import supabase

# models
from app.models import *

# services
from app.services.game.game_domain import get_expires_in_by_game_mode

# utils
from app.utils.helpers import calculate_minutes_to_seconds


def get_all_song_titles(db: Session) -> list[str]:
    """
    Retrieve an alphabetically ordered list of all song titles.
    """

    # Query only song titles and sort them alphabetically
    query = select(Song.title).order_by(Song.title)

    song_titles = db.scalars(query).all()

    # Extract titles from the query result
    return [title for title in song_titles]


def get_random_song(db: Session) -> Song | None:
    """
    Retrieve a randomly selected song from the database.

    Returns:
        A random song, or None if no songs are available.
    """

    # Randomize song order and select the first result
    query = select(Song).order_by(func.random())

    return db.scalars(query).first()


def get_signed_audio_link(mode: str, audio_link: str) -> str:
    """
    Obtain a signed URL for the song audio clip based on game mode expiry.
    """

    # Determine the expiration duration based on game mode
    expires_in_minutes = get_expires_in_by_game_mode(mode)

    # Convert expiration duration to seconds
    expires_in_seconds = calculate_minutes_to_seconds(expires_in_minutes)

    # Create a signed URL for the audio file in storage
    link_data = supabase.storage.from_("songs").create_signed_url(
        audio_link,
        expires_in_seconds,
    )

    return link_data["signedUrl"]
