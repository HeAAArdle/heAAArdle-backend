from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.statistics import Statistics
from app.models.enums import modes
from app.services.password_hasher import hash_password
from app.services.token_generator import generate_token
from app.services.password_hasher import verify_password

def sign_up(db: Session, username: str, password: str):
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        user = User(username=username, password=hash_password(password))

        db.add(user)
        db.flush()

        for mode in ("original", "daily"):
            stats = Statistics(userID=user.userID, mode=mode)
            db.add(stats)

        token = generate_token()
        user.token = token

        db.commit()
        return user, token
    except Exception:
        db.rollback()
        raise

def sign_in(db: Session, username: str, password: str):
    try:
        user = db.query(User).filter(User.username == username).first()

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token = generate_token()
        user.token = token

        db.commit()
        return user, token
    except Exception:
        db.rollback()
        raise

def get_current_user(token: str, db: Session):
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401)
    return user
