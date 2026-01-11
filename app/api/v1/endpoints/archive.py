# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# schemas
from app.schemas.game import GetArchivedDailyGameResultsResponse

# services
from app.services.archive import (
    InvalidYearOrMonth,
    get_archived_daily_game_results_service,
)


router = APIRouter()


@router.get(
    "/?year={year}&month={month}", response_model=GetArchivedDailyGameResultsResponse
)
def get_archived_daily_game_results(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_user),  # Uncomment once auth is available
):
    # Use a placeholder user ID until authentication is available
    user_id = "TEMPORARY_USER_ID"

    try:
        return get_archived_daily_game_results_service(year, month, db, user_id)

    except InvalidYearOrMonth:
        raise HTTPException(400, "Invalid year or month.")
