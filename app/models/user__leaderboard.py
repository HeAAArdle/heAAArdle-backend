from sqlalchemy import Integer, ForeignKey, ForeignKeyConstraint

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.leaderboard import Leaderboard

from app.models.enums import modes, period

class UserLeaderboard(Base):
    __tablename__ = "user_leaderboard"

    userID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.userID", ondelete="CASCADE"), primary_key=True
    )
    mode:   Mapped[str] = mapped_column(modes, primary_key=True)
    period: Mapped[str] = mapped_column(period, primary_key=True)

    numberOfWins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships

    user: Mapped["User"] = relationship(
        back_populates="user_leaderboards"
    )

    leaderboard: Mapped["Leaderboard"] = relationship(
        back_populates="user_leaderboards"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["mode", "period"],
            ["leaderboards.mode", "leaderboards.period"]
        ),
    )