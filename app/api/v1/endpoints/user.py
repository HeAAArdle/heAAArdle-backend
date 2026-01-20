from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.account import (SignUpRequest, SignUpResponse, SignInResponse)
from app.services.user.authentication import sign_up, sign_in, sign_out
from app.services.user.user_dependencies import get_current_user
from app.services.user.delete import delete_user


router = APIRouter()

@router.post("/signup/", response_model=SignUpResponse, status_code=201)
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    """
    Registers a new user and returns their username and token.
    """
    user, token = sign_up(db, req.username, req.password)
    return SignUpResponse(username=user.username, token=token)

@router.post("/signin/", response_model=SignInResponse)
def signin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Signs in a user.
    """
    user, token = sign_in(db, form_data.username, form_data.password)
    return SignInResponse(access_token=token, token_type="bearer")

@router.post("/signout/")    
def signout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/user/signin"))):
    """
    Signs out a user.
    """
    return sign_out(token)

@router.delete("/delete")
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Permanently deletes the authenticated user's account and all related data.
    """
    delete_user(db, current_user.userID)
