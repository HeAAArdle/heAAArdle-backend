from pydantic import BaseModel
from datetime import date
from typing import Literal, List, Optional

class SubmitGameRequest(BaseModel):
    gameSessionID: str
    gameMode: Literal["original", "daily"]
    won: bool
    guessCount : int
    date : date | None

class GetArchivedDailyGameResultsResponse(BaseModel):
    numberOfDays: int
    startingDay: int
    results: List[Optional[bool]]

class UserWins(BaseModel):
    username: str
    wins: int

class GetLeaderboardDataOriginal(BaseModel):
    daily: List[UserWins]
    weekly: List[UserWins]
    monthly: List[UserWins]
    allTime: List[UserWins]

class GetLeaderboardDataDaily(BaseModel):
    weekly: List[UserWins]
    monthly: List[UserWins]
    allTime: List[UserWins]

class GetLeaderboardDataResponse(BaseModel):
    original: GetLeaderboardDataOriginal
    daily: GetLeaderboardDataDaily