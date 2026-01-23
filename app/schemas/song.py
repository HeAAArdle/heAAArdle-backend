import uuid

from typing import Annotated, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class GetAllSongResponse(BaseModel):
    title: str

    model_config = ConfigDict(from_attributes=True)


class SongMetadata(BaseModel):
    type: Literal["song metadata"]
    title: str
    releaseYear: Annotated[int, Field(ge=1)]
    album: str
    shareLink: Annotated[str, Field(min_length=1)]
    artists: List[str]
    songID: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
