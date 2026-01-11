from pydantic import BaseModel, ConfigDict, AnyUrl, conint, model_validator

from app.schemas.enums import GameMode, SubmittableGameMode

import uuid

from datetime import date as DateType

from typing import List, Literal, Optional, Annotated, Self, Union


class StartGameRequest(BaseModel):
    userID: Optional[uuid.UUID]
    mode: GameMode
    game_date: Optional[DateType]


class StartGameResponse(BaseModel):
    wsGameSessionID: str
    wsURL: Annotated[str, AnyUrl]
    expiresIn: Annotated[int, conint(ge=0)]
    audio: Annotated[str, AnyUrl]
    startAt: Annotated[int, conint(ge=0)]
    date: Optional[DateType] # null for non-daily modes

    model_config = ConfigDict(from_attributes=True)


class SubmitGameRequest(BaseModel):
    wsGameSessionID: str
    userID: Optional[uuid.UUID]
    mode: SubmittableGameMode
    won: bool
    attempts: Annotated[int, conint(ge=1)]
    game_date: Optional[DateType]

    @model_validator(mode='after')
    def validate_mode_and_date(self) -> Self:
        mode = self.mode
        game_date = self.game_date

        if mode == "daily" and game_date is None:
            raise ValueError("Daily mode requires a date.")

        if mode == "original" and game_date is not None:
            raise ValueError("Original mode must not have a date.")

        return self


class UnavailableDay(BaseModel):
    date: DateType
    available: Literal[False]
    result: None


class AvailableDay(BaseModel):
    date: DateType
    available: Literal[True]
    result: Optional[bool]


Day = Union[AvailableDay, UnavailableDay]


class GetArchivedDailyGameResultsResponse(BaseModel):
    numberOfDays: int
    startingDay: int
    days: List[Day]

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
