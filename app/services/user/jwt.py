from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from app.core.config import settings

SECRET_KEY = settings.supabase_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


def create_access_token(
    data: dict[str, str | datetime], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a JWT access token with an optional expiration.

    Returns:
        A JWT-encoded string representing the access token.

    Raises:
        AssertionError: If SECRET_KEY is not configured.
    """

    assert SECRET_KEY is not None

    to_encode = dict(data)

    # Determine expiration time of token

    # Use the provided expiration delta, otherwise fall back to the default
    expire = datetime.now() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Add the expiration claim to the payload
    to_encode.update({"exp": expire})

    # Encode and return the JWT using the configured algorithm (HS256)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[dict[str, str | datetime]]:
    """
    Verify and decode a JWT access token.

    Returns:
        The decoded payload as a dictionary if the token is valid, otherwise None.

    Raises:
        AssertionError: If SECRET_KEY is not configured.
    """

    assert SECRET_KEY is not None

    try:
        # Decode the JWT and validate its signature and expiration time
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Return the decoded payload if verification succeeds
        return payload

    except JWTError:
        # Return None if the token is invalid, expired, or malformed
        return None
