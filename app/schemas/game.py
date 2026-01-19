from pydantic import BaseModel, ConfigDict, HttpUrl, AnyWebsocketUrl, Field

from app.schemas.enums import GameMode, SubmittableGameMode

from datetime import date as DateType

from typing import List, Literal, Optional, Annotated, Union


class StartGameRequest(BaseModel):
    mode: GameMode
    date: Optional[DateType]


class BaseStartGameResponse(BaseModel):
    wsGameSessionID: str
    wsURL: AnyWebsocketUrl
    expiresInMinutes: Annotated[int, Field(ge=0)]
    date: Optional[DateType]


class AudioStartGameResponse(BaseStartGameResponse):
    mode: Literal[
        GameMode.ORIGINAL,
        GameMode.DAILY,
        GameMode.RAPID,
        GameMode.ARCHIVE,
    ]
    audio: HttpUrl
    audioStartAt: Annotated[int, Field(ge=0)]


class LyricsStartGameResponse(BaseStartGameResponse):
    mode: Literal[GameMode.LYRICS]
    lyrics: str


StartGameResponse = Annotated[
    Union[AudioStartGameResponse, LyricsStartGameResponse], Field(discriminator="mode")
]


class SubmitGameRequest(BaseModel):
    wsGameSessionID: str
    mode: SubmittableGameMode
    won: bool
    attempts: Annotated[int, Field(ge=1, le=6)]


class SubmitGameResponse(BaseModel):
    mode: SubmittableGameMode
    won: bool
    attempts: Annotated[int, Field(ge=1, le=6)]
    title: str
    releaseYear: Annotated[int, Field(ge=1)]
    album: str
    shareLink: HttpUrl
    artists: List[str]

    model_config = ConfigDict(from_attributes=True)


class UnavailableDay(BaseModel):
    date: DateType
    available: Literal[False]
    result: None


class AvailableDay(BaseModel):
    date: DateType
    available: Literal[True]
    result: Optional[bool]


Day = Annotated[
    Union[AvailableDay, UnavailableDay], Field(discriminator="available")
]


class GetArchivedDailyGameResultsResponse(BaseModel):
    numberOfDays: Annotated[int, Field(ge=1, le=31)]
    startingDay: Annotated[int, Field(ge=0, le=6)]
    days: List[Day]

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)
