from pydantic import BaseModel
from typing import Tuple

class GetUserStatisticsRequest(BaseModel):
    token: str

class GameDetails(BaseModel):
    gamesPlayed: int
    winCount: int
    winPercentage: int
    currentStreak: int
    maximumStreak: int
    guessDistribution: Tuple[int, int, int, int, int, int]

class GetUserStatisticsResponse(BaseModel):
    original: GameDetails
    daily: GameDetails

class GetUserResponse(BaseModel):
    username: str
    token: str

class SignInRequest(BaseModel):
    username: str
    password: str

class SignInResponse(BaseModel):
    username: str
    token: str

class SignUpRequest(BaseModel):
    username: str
    password: str

class SignUpResponse(BaseModel):
    username: str
    token: str