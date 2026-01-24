# FastAPI
from fastapi import APIRouter, Depends

# SQLAlchemy
from sqlalchemy.orm import Session

# app core
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

from app.services.user.user_dependencies import get_current_user, oauth2_scheme

router = APIRouter()


@router.post("/signup/", response_model=SignUpResponse, status_code=201)
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Returns:
        The created user's username and an authentication token.
    """

    # Create a new user and issue an authentication token
    user, token = sign_up(db, req.username, req.password)

    return SignUpResponse(username=user.username, token=token)


@router.post("/signin/", response_model=SignInResponse)
def signin(req: SignUpRequest, db: Session = Depends(get_db)):
    """
    Authenticate an existing user and issue an access token.
    """

    # Validate credentials and generate a new access token
    _, token = sign_in(db, req.username, req.password)

    return SignInResponse(access_token=token, token_type="bearer")


@router.post("/signout/")
def signout(token: str = Depends(oauth2_scheme)):
    """
    Signs a user out.
    """

    return sign_out(token)


@router.delete("/delete")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Permanently delete the authenticated user's account.

    This operation removes the user and all associated data.
    """

    # Delete the user and all related records from the database
    delete_user(db, current_user.userID)


@router.post("/get_user")
def get_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Retrieve the currently authenticated user's information.
    """

    # Resolve and return the authenticated user from the token
    user = get_current_user(token, db)

    return user
