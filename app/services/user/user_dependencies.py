from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.user.jwt import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/signin")


def resolve_user(
    token: str,
    db: Session,
    required: bool = True,
) -> User | None:
    payload = verify_access_token(token)

    if not payload:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            )

        return None

    user = db.query(User).filter(User.userID == payload.get("user_id")).first()

    if not user and required:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieves the current user based on the provided authentication token.
    Raises if the user does not exist.
    """

    return resolve_user(token, db, required=True)


def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Retrieves the current user based on the provided authentication token.
    Return None if the user does not exist.
    """

    return resolve_user(token, db, required=False)
