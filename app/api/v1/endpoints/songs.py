from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.db.get_db import get_db

from app.models.song import Song

from app.schemas.song import GetAllSongResponse

router = APIRouter()

@router.get("/songs", response_model=list[GetAllSongResponse])
def get_all_songs(db: Session = Depends(get_db)):
    # Query all songs ordered by title
    songs = db.query(Song).order_by(Song.title).all()

    return songs