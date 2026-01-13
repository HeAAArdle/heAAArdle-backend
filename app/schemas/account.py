from pydantic import BaseModel
from typing import Tuple

class GetUserStatisticsRequest(BaseModel):
    token: str | None

class Statistics(BaseModel):
    gamesPlayed: int
    winCount: int
    winPercentage: int
    currentStreak: int
    maximumStreak: int
    guessDistribution: Tuple[int, int, int, int, int, int]

class GetUserStatisticsResponse(BaseModel):
    original: Statistics
    daily: Statistics

class GetUserResponse(BaseModel):
    username: str
    token: str | None

class SignInRequest(BaseModel):
    username: str
    password: str

class SignInResponse(BaseModel):
    username: str
    token: str | None

class SignUpRequest(BaseModel):
    username: str
    password: str

class SignUpResponse(BaseModel):
    username: str
    token: str | None