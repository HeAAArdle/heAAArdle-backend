from sqlalchemy import Integer, ForeignKey

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuid

from app.db.base import Base

from app.models.user import User

from enums import modes

class Statistics(Base):
    __tablename__ = "statistics"

    mode:          Mapped[str] = mapped_column(modes, nullable=False, index=True)
    gamesPlayed:   Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    winCount:      Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    currentStreak: Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    maximumStreak: Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    guesses1:      Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    guesses2:      Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    guesses3:      Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    guesses4:      Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    guesses5:      Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    guesses6:      Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)

    # Foreign Keys

    userID: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.userID"), primary_key=True
    )

    # Relationships

    # Statistics <-> User: One-to-One
    user: Mapped["User"] = relationship("User", back_populates="statistics")