from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes the password using the bcrypt algorithm.
    """

    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies a password against its hashed version.
    """

    return pwd_context.verify(password, hashed)
