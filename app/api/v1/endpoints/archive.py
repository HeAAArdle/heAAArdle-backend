# standard library
from typing import Optional

# FastAPI
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
from app.db.get_db import get_db

# models
from app.models.user import User

# schemas
from app.schemas.archive import GetArchivedDailyGameResultsResponse

# services
from app.services.archive.archive import get_archived_daily_game_results_service

from app.services.user.user_dependencies import get_optional_user

# exceptions
from app.services.exceptions import InvalidYearOrMonth

router = APIRouter()


@router.get("/", response_model=GetArchivedDailyGameResultsResponse)
def get_archived_daily_game_results(
    year: int,
    month: int,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    user_id = user.userID if user else None

    try:
        return get_archived_daily_game_results_service(year, month, db, user_id)

    except InvalidYearOrMonth:
        raise HTTPException(400, "Invalid year or month.")
