from pydantic import BaseModel, ConfigDict


class GetAllSongResponse(BaseModel):
    title: str

    model_config = ConfigDict(from_attributes=True)
