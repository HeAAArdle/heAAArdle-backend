from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.statistics import Statistics
from app.services.authentication.authentication_password import hash_password, verify_password
from app.services.authentication.jwt import create_access_token

def sign_up(db: Session, username: str, password: str):
    """
    Registers a new user and returns the user object along with an authentication token.
    """
    # Check if username already exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    # Create new user with hashed password
    user = User(username=username, password=hash_password(password))
    db.add(user)
    db.flush()

    # Initialize statistics for the new user in all modes
    stats_objects = [
        Statistics(userID=user.userID, mode="original"),
        Statistics(userID=user.userID, mode="daily"),
    ]
    db.add_all(stats_objects)
    
    # Generate authentication token
    token = create_access_token({"user_id": str(user.userID)})
    db.commit()
    return user, token


def sign_in(db: Session, username: str, password: str):
    """
    Authenticates a user and returns the user object along with a new authentication token.
    """
    # Look up user by username
    user = db.query(User).filter(User.username == username).first()
    
    # Verify if user exists and valid password
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate new authentication token
    token = create_access_token({"user_id": str(user.userID)})
    return user, token


def sign_out(token: str):
    return {"message": "Sign out successful, discard the token on client side"}