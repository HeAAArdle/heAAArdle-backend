from pydantic import BaseModel

class GetAllSongResponse(BaseModel):
    title: str

    class Config:
        from_attributes = True