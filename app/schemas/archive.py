# standard library
from datetime import date as DateType

from typing import Annotated, List, Literal, Optional, Union

# schemas
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class UnavailableDay(BaseModel):
    date: DateType
    available: Literal[False]
    result: None


class AvailableDay(BaseModel):
    date: DateType
    available: Literal[True]
    result: Optional[bool]


Day = Annotated[Union[AvailableDay, UnavailableDay], Field(discriminator="available")]


class GetArchivedDailyGameResultsResponse(BaseModel):
    numberOfDays: Annotated[int, Field(ge=1, le=31)]
    numberOfDaysOfPreviousMonth: Annotated[int, Field(ge=1, le=31)]
    startingDay: Annotated[int, Field(ge=0, le=6)]
    days: List[Day]

    model_config = ConfigDict(from_attributes=True)
