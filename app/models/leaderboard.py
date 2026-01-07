from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from enums import modes, period

class Leaderboard(Base):
    __tablename__ = "leaderboards"

    mode   : Mapped[str] = mapped_column(modes, primary_key=True)
    period : Mapped[str] = mapped_column(period, primary_key=True)

    # Relationships

    users = relationship("User", secondary="user_is_ranked_in_leaderboard", back_populates="leaderboards")
