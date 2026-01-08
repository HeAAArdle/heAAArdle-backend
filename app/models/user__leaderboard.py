from sqlalchemy import Integer, ForeignKey

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

from app.models.user import User
from app.models.leaderboard import Leaderboard

from enums import modes, period

class UserLeaderboard(Base):
    __tablename__ = "user_leaderboard"

    userID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.userID"), primary_key=True
    )
    mode:   Mapped[str] = mapped_column(modes, ForeignKey("leaderboards.mode"), primary_key=True)
    period: Mapped[str] = mapped_column(period, ForeignKey("leaderboards.period"), primary_key=True)

    numberOfWins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships

    user: Mapped["User"] = relationship(
        back_populates="user_leaderboards"
    )

    leaderboard: Mapped["Leaderboard"] = relationship(
        back_populates="user_leaderboards"
    )