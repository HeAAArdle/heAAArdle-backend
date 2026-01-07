from sqlalchemy import Column, String

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

import uuid

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    userID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # Relationships

    game_sessions = relationship("GameSession", back_populates="user", uselist=False)
    leaderboards = relationship("Leaderboard", secondary="user_is_ranked_in_leaderboard", back_populates="users")