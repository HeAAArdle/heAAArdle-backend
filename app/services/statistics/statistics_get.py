# standard library
from uuid import UUID

# SQLAlchemy
from sqlalchemy import select

from sqlalchemy.orm import Session

# models
from app.models.statistics import Statistics


def get_db_statistics(db: Session, user_id: UUID) -> dict[str, Statistics]:
    """
    Retrieve statistics, separated by mode, for a given user from the database.
    """

    query = select(Statistics).where(Statistics.userID == user_id)

    statistics = db.scalars(query).all()

    return {statistic.mode: statistic for statistic in statistics}
