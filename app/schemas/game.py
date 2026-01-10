from pydantic import BaseModel
from datetime import date
from typing import Literal, List, Optional

class StartGameRequest(BaseModel):
    mode: Literal["original", "daily", "rapid", "lyrics"]
    userID: Optional[str]

class SubmitGameRequest(BaseModel):
    gameSessionID: str
    gameMode: Literal["original", "daily"]
    won: bool
    attempts: int
    date: Optional[date]

class GetArchivedDailyGameResultsResponse(BaseModel):
    numberOfDays: int
    startingDay: int
    results: List[Optional[bool]]

    class Config:
        from_attributes = True

class UserWins(BaseModel):
    username: str
    wins: int

class GetLeaderboardDataOriginal(BaseModel):
    daily: UserWins
    weekly: UserWins
    monthly: UserWins
    allTime: UserWins

class GetLeaderboardDataDaily(BaseModel):
    weekly: UserWins
    monthly: UserWins
    allTime: UserWins

class GetLeaderboardDataResponse(BaseModel):
    original: GetLeaderboardDataOriginal
    daily: GetLeaderboardDataDaily

    class Config:
        from_attributes = True