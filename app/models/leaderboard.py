from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from app.models.enums import modes, period

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user__leaderboard import UserLeaderboard

class Leaderboard(Base):
    __tablename__ = "leaderboards"

    mode:   Mapped[str] = mapped_column(modes, primary_key=True)
    period: Mapped[str] = mapped_column(period, primary_key=True)

    # Relationships

    # Leaderboard <-> User: Many-to-Many
    user_leaderboards: Mapped[list["UserLeaderboard"]] = relationship(
        back_populates="leaderboard"
    )