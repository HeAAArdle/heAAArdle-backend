# FastAPI
from fastapi import APIRouter, Depends

# SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# models
from app.models.song import Song

# schemas
from app.schemas.song import GetAllSongResponse


router = APIRouter()


@router.get("/songs", response_model=list[GetAllSongResponse])
def get_all_songs(db: Session = Depends(get_db)):
    # Query all songs ordered by title
    query = select(Song).order_by(Song.title)

    songs = db.scalars(query).all()

    return songs
