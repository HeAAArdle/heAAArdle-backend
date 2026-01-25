# standard library
from typing import Annotated, Tuple

# schemas
from pydantic import BaseModel, Field


class GetUserStatisticsRequest(BaseModel):
    token: str


class Statistics(BaseModel):
    gamesPlayed: Annotated[int, Field(ge=0)]
    winCount: Annotated[int, Field(ge=0)]
    winPercentage: Annotated[int, Field(ge=0, le=100)]
    currentStreak: Annotated[int, Field(ge=0)]
    maximumStreak: Annotated[int, Field(ge=0)]
    guessDistribution: Tuple[
        Annotated[int, Field(ge=0)],
        Annotated[int, Field(ge=0)],
        Annotated[int, Field(ge=0)],
        Annotated[int, Field(ge=0)],
        Annotated[int, Field(ge=0)],
        Annotated[int, Field(ge=0)],
    ]


class GetUserStatisticsResponse(BaseModel):
    original: Statistics
    daily: Statistics
