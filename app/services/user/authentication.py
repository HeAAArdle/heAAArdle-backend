# FastAPI
from fastapi import HTTPException, status

# SQLAlchemy
from sqlalchemy.orm import Session

# models
from app.models.leaderboard import Leaderboard

from app.models.statistics import Statistics

from app.models.user import User

from app.models.user__leaderboard import UserLeaderboard

# services
from app.schemas.enums import GameMode

from app.services.user.jwt import create_access_token

from app.services.user.password import hash_password, verify_password


def sign_up(db: Session, username: str, password: str):
    """
    Register a new user and returns the user object along with an authentication token.
    """

    # Check if username already exists
    existing = db.query(User).filter(User.username == username).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another user already has this username.",
        )

    # Create new user with hashed password
    user = User(username=username, password=hash_password(password))

    db.add(user)

    db.flush()

    # Initialize statistics for the new user in all modes
    db.add_all(
        [
            Statistics(userID=user.userID, mode=GameMode.ORIGINAL),
            Statistics(userID=user.userID, mode=GameMode.DAILY),
        ]
    )

    # Initialize leaderboard entries for the new user in all leaderboard types
    leaderboards = db.query(Leaderboard).all()

    db.add_all(
        [
            UserLeaderboard(
                userID=user.userID, mode=lb.mode, period=lb.period, numberOfWins=0
            )
            for lb in leaderboards
        ]
    )

    # Generate authentication token
    token = create_access_token({"user_id": str(user.userID)})

    db.commit()

    return user, token


def sign_in(db: Session, username: str, password: str):
    """
    Authenticate a user and returns the user object along with a new authentication token.
    """

    # Look up user by username
    user = db.query(User).filter(User.username == username).first()

    # Verify if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A user with this username does not exist.",
        )

    # Check the correctness of the provided password
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )

    # Generate new authentication token
    token = create_access_token({"user_id": str(user.userID)})

    return user, token


def sign_out(token: str):
    return {"message": "Sign out successful; discard the token on client side."}
