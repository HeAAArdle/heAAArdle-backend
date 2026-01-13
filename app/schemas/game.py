from pydantic import BaseModel, ConfigDict, AnyUrl, Field, model_validator

from app.schemas.enums import GameMode, SubmittableGameMode

from datetime import date as DateType

from typing import List, Literal, Optional, Annotated, Self, Union


class StartGameRequest(BaseModel):
    mode: GameMode
    date: Optional[DateType]


class StartGameResponse(BaseModel):
    wsGameSessionID: str
    wsURL: Annotated[str, AnyUrl]
    expiresIn: Annotated[int, Field(ge=0)]
    audio: Optional[str]
    startAt: Optional[Annotated[int, Field(ge=0)]]
    lyrics: Optional[str]
    date: Optional[DateType] # null for non-daily modes

    model_config = ConfigDict(from_attributes=True)


class SubmitGameRequest(BaseModel):
    wsGameSessionID: str
    mode: SubmittableGameMode
    date: Optional[DateType]
    won: bool
    attempts: Annotated[int, Field(ge=1,le=6)]

    @model_validator(mode='after')
    def validate_mode_and_date(self) -> Self:
        mode = self.mode
        date = self.date

        if mode == "daily" and date is None:
            raise ValueError("Daily mode requires a date.")

        if mode == "original" and date is not None:
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
    numberOfDays: Annotated[int, Field(ge=1, le=31)]
    startingDay: Annotated[int, Field(ge=0, le=6)]
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
