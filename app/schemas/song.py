from pydantic import BaseModel
from datetime import date

class GetAllSongResponse(BaseModel):
    title: str

class GetRandomSongResponse(BaseModel):
    songID: str
    title: str
    artist: str
    releaseYear: int
    album: str | None
    audio: str
    link: str

class GetDailySongResponse(BaseModel):
    songID: str
    title: str
    artist: str
    releaseYear: int
    album: str | None
    audio: str
    link: str

class GetArchivedDailySongResponse(BaseModel):
    songID: str
    title: str
    artist: str
    releaseYear: int
    album: str | None
    date: date
    audio: str
    link: str

class GetLyricsModeSongResponse(BaseModel):
    songID: str
    title: str
    artist: str
    releaseYear: int
    album: str | None
    lyrics: str
    link: str