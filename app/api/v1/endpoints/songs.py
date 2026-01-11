# FastAPI
from fastapi import APIRouter, Depends

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# models

# schemas
from app.schemas.song import GetAllSongResponse

# utils
from app.services.song import get_all_song_titles


router = APIRouter()


@router.get("/songs", response_model=list[GetAllSongResponse])
def get_all_songs(db: Session = Depends(get_db)):
    # Get an ordered list of titles
    titles = get_all_song_titles(db)

    return [{"title": t} for t in titles]
