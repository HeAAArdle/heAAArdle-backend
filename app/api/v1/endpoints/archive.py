# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# models
from app.models.game_session import GameSession

# schemas
from app.schemas.game import (
    UnavailableDay,
    AvailableDay,
    Day,
    GetArchivedDailyGameResultsResponse,
)

# standard library
import calendar

from datetime import date

from typing import List, cast


router = APIRouter()


@router.get(
    "/?year={year}&month={month}", response_model=GetArchivedDailyGameResultsResponse
)
def get_archived_daily_game_results(
    year: int, month: int, db: Session = Depends(get_db)
):
    # Validate year + month
    try:
        starting_day, number_of_days = calendar.monthrange(year, month)
    except:
        raise HTTPException(status_code=400, detail="Invalid year or month.")

    # Load all played days for that month
    query = (
        select(GameSession)
        .where(func.extract("year", GameSession.date) == year)
        .where(func.extract("month", GameSession.date) == month)
    )

    archived_daily_game_results = db.scalars(query).all()

    # Creates a dictionary formatted as:
    # {
    #   date(...): GameSession(...),
    # }

    played_days = cast(
        dict[date, GameSession],
        {daily_game.date: daily_game for daily_game in archived_daily_game_results},
    )

    days: List[Day] = []

    # Iterate every calendar day in the month
    for day in range(1, number_of_days + 1):

        current_date = date(year, month, day)

        if current_date in played_days:
            daily_game = played_days[current_date]

            mapping = {"win": True, "lose": False}

            result = mapping.get(daily_game.result)
            
            days.append(
                AvailableDay(
                    date=current_date, available=True, result=result
                )
            )

        else:
            days.append(UnavailableDay(date=current_date, available=False, result=None))

    return GetArchivedDailyGameResultsResponse(
        numberOfDays=number_of_days, startingDay=starting_day, days=days
    )
