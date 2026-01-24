# standard library
from typing import Optional

# FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# SQLAlchemy
from sqlalchemy.orm import Session

# app core / db
from app.db.session import get_db

# models
from app.models.user import User

# services
from app.services.user.jwt import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/user/signin",
    auto_error=False,
)


def resolve_user(token: Optional[str], db: Session, required: bool) -> Optional[User]:
    """
    Resolve a user from an authentication token.

    Raises:
        HTTPException: If authentication is required and the token is missing, invalid, expired, or does not resolve to a user.
    """

    # Reject missing token when authentication is required
    if token is None:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated."
            )

        return None

    # Verify the token and decode its payload
    payload = verify_access_token(token)

    # Reject invalid or expired tokens when authentication is required
    if not payload:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            )

        return None

    # Extract the user identifier from the token payload
    user_id = payload.get("user_id")

    # Reject malformed token payloads when authentication is required
    if user_id is None:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
            )

        return None

    # Look up the user associated with the token
    user = db.query(User).filter(User.userID == user_id).first()

    # Reject references to a non-existent user
    if not user and required:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )

    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve the currently authenticated user.

    Raises:
        HTTPException: If authentication fails or the user does not exist.
    """

    return resolve_user(token, db, required=True)


def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Attempt to retrieve the currently authenticated user.

    Returns:
        The resolved user, or None if authentication is not provided or invalid.
    """

    return resolve_user(token, db, required=False)
