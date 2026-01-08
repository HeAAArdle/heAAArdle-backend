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