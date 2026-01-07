from sqlalchemy import Column, Integer, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

from enums import modes

class Statistics(Base):
    __tablename__ = "statistics"

    mode: Mapped[str] = mapped_column(modes, index=True, nullable=False)
    gamesPlayed       = Column(Integer, index=True, nullable=False, default=0)
    winCount          = Column(Integer, index=True, nullable=False, default=0)
    currentStreak     = Column(Integer, index=True, nullable=False, default=0)
    maximumStreak     = Column(Integer, index=True, nullable=False, default=0)
    guesses1          = Column(Integer, index=True, nullable=False, default=0)
    guesses2          = Column(Integer, index=True, nullable=False, default=0)
    guesses3          = Column(Integer, index=True, nullable=False, default=0)
    guesses4          = Column(Integer, index=True, nullable=False, default=0)
    guesses5          = Column(Integer, index=True, nullable=False, default=0)
    guesses6          = Column(Integer, index=True, nullable=False, default=0)

    # Foreign Keys

    userID = Column(UUID(as_uuid=True), ForeignKey("users.userID"), primary_key=True)

    # Relationships

    user = relationship("User", back_populates="statistics")