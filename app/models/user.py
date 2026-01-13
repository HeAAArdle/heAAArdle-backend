from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

from app.models.game_session import GameSession
from app.models.user__leaderboard import UserLeaderboard

class User(Base):
    __tablename__ = "users"

    userID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships

    # User <-> GameSession: One-to-Many
    game_sessions: Mapped["GameSession"] = relationship( # type: ignore
        "GameSession", back_populates="user", uselist=False
    )

    # User <-> Statistics: One-to-One
    statistics: Mapped["Statistics"] = relationship( # type: ignore
        "Statistics", back_populates="user"
    )

    # User <-> Leaderboard: Many-to-Many
    user_leaderboards: Mapped[list["UserLeaderboard"]] = relationship( # type: ignore
        back_populates="user"
    )