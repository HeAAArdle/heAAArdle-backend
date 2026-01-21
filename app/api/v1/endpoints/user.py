# FastAPI
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# SQLAlchemy
from sqlalchemy.orm import Session

# app core / db
from app.db.session import get_db

# models
from app.models.user import User

# schemas
from app.schemas.account import (
    SignInResponse,
    SignUpRequest,
    SignUpResponse,
)

# services
from app.services.user.authentication import sign_in, sign_out, sign_up
from app.services.user.delete import delete_user
from app.services.user.user_dependencies import get_current_user

router = APIRouter()

@router.post("/signup/", response_model=SignUpResponse, status_code=201)
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    """
    Registers a new user and returns their username and token.
    """
    user, token = sign_up(db, req.username, req.password)
    return SignUpResponse(username=user.username, token=token)

@router.post("/signin/", response_model=SignInResponse)
def signin(req: SignUpRequest, db: Session = Depends(get_db)):
    """
    Signs a user in.
    """
    _, token = sign_in(db, req.username, req.password)
    return SignInResponse(access_token=token, token_type="bearer")

@router.post("/signout/")    
def signout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/user/signin"))):
    """
    Signs a user out.
    """
    return sign_out(token)

@router.delete("/delete")
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Permanently deletes the authenticated user's account and all related data.
    """
    delete_user(db, current_user.userID)

@router.post("/user")
def get_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/user/signin")), db: Session = Depends(get_db)):
    """
    Retrieves the user information of the authenticated user.
    """
    user = get_current_user(token, db)
    return user