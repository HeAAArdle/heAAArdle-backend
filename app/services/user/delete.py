from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from uuid import UUID


def delete_user(db: Session, user_id: UUID):
    """
    Permanently remove a user from the database.
    Raises an HTTPException if the user does not exist.
    """
    # Attempt to retrieve the user by ID
    user = db.get(User, user_id)

    # If the user does not exist, raise a 404 error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    db.delete(user)

    db.commit()
