from pydantic import BaseModel, Field
from typing import Annotated, Tuple


class GetUserStatisticsRequest(BaseModel):
    token: str


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
    token: str


class SignInRequest(BaseModel):
    username: str
    password: str


class SignInResponse(BaseModel):
    access_token: str
    token_type: str


class SignUpRequest(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=36)]
    password: Annotated[str, Field(min_length=8, max_length=72)]


class SignUpResponse(BaseModel):
    username: str
    token: str
