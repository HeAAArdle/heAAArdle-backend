from pydantic import BaseModel, ConfigDict, AnyUrl, conint, model_validator

from app.schemas.enums import GameMode, SubmittableGameMode

import uuid

from datetime import date

from typing import List, Optional, Annotated, Self


class StartGameRequest(BaseModel):
    mode: GameMode
    userID: Optional[uuid.UUID]


class StartGameResponse(BaseModel):
    wsGameSessionID: str
    expiresIn: Annotated[int, conint(ge=0)]
    wsURL: Annotated[str, AnyUrl]
    audio: Annotated[str, AnyUrl]
    startAt: Annotated[int, conint(ge=0)]
    date: Optional[date]  # null for non-daily modes

    model_config = ConfigDict(from_attributes=True)


class SubmitGameRequest(BaseModel):
    wsGameSessionID: str
    userID: Optional[uuid.UUID]
    mode: SubmittableGameMode
    won: bool
    attempts: Annotated[int, conint(ge=1)]
    date: Optional[date]

    @model_validator(mode='after')
    def validate_mode_and_date(self) -> Self:
        mode = self.mode
        date = self.date

        if mode == "daily" and date is None:
            raise ValueError("Daily mode requires a date.")

        if mode == "original" and date is not None:
            raise ValueError("Original mode must not have a date.")

        return self

class GetArchivedDailyGameResultsResponse(BaseModel):
    numberOfDays: int
    startingDay: int
    results: List[Optional[bool]]

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)
