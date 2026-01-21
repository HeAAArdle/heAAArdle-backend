from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from uuid import UUID


def delete_user(db: Session, user_id: UUID):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
