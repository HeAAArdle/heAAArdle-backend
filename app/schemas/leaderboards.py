# standard library
from typing import Annotated, List, Optional

# schemas
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class LeaderboardRow(BaseModel):
    username: str
    isUser: bool = False
    numberOfWins: Annotated[int, Field(ge=0)]
    rank: Optional[Annotated[int, Field(ge=1)]] = None


class GetLeaderboardDataOriginal(BaseModel):
    daily: List[LeaderboardRow]
    weekly: List[LeaderboardRow]
    monthly: List[LeaderboardRow]
    allTime: List[LeaderboardRow]


class GetLeaderboardDataDaily(BaseModel):
    weekly: List[LeaderboardRow]
    monthly: List[LeaderboardRow]
    allTime: List[LeaderboardRow]


class GetLeaderboardDataResponse(BaseModel):
    original: GetLeaderboardDataOriginal
    daily: GetLeaderboardDataDaily

    model_config = ConfigDict(from_attributes=True)
