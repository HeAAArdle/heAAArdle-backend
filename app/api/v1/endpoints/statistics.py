from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.account import (GetUserStatisticsRequest, GetUserStatisticsResponse)
from app.services.statistics_service import get_db_statistics
from app.services.statistics_mapper import dbstats_to_schemastats
from app.db.session import get_db
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/", response_model=GetUserStatisticsResponse)
def get_user_statistics_endpoint(req: GetUserStatisticsRequest, db: Session = Depends(get_db)):
    user = get_current_user(req.token, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user_statistics(db, user.id)

def get_user_statistics(db: Session, user_id: str) -> GetUserStatisticsResponse:
    stats = get_db_statistics(db, user_id)

    try:
        original = stats["original"]
        daily = stats["daily"]
    except KeyError:
        raise ValueError("Statistics missing")

    return GetUserStatisticsResponse(
        original=dbstats_to_schemastats(original),
        daily=dbstats_to_schemastats(daily),
    )
