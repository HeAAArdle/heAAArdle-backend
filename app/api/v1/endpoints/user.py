from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.account import (
    SignUpRequest,
    SignUpResponse,
    SignInRequest,
    SignInResponse,
)
from app.services.auth_service import sign_up, sign_in

router = APIRouter()

@router.post("/signup/", response_model=SignUpResponse, status_code=201)
def signup(
    req: SignUpRequest,
    db: Session = Depends(get_db),
):
    user, token = sign_up(db, req.username, req.password)

    return SignUpResponse(
        username=user.username,
        token=token,
    )

@router.post("/signin/", response_model=SignInResponse)
def signin(
    req: SignInRequest,
    db: Session = Depends(get_db),
):
    user, token = sign_in(db, req.username, req.password)

    return SignInResponse(
        username=user.username,
        token=token,
    )
