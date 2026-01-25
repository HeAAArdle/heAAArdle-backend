# standard library
from typing import List, Optional

# schemas
from pydantic import (
    BaseModel,
    ConfigDict,
)


class LeaderboardRow(BaseModel):
    username: str
    isUser: bool = False
    numberOfWins: int
    rank: Optional[int] = None


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
