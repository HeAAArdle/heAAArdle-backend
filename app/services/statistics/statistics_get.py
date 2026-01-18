from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.statistics import Statistics

def get_db_statistics(db: Session, user_id: UUID) -> dict[str, Statistics]:
    """
    Retrieves statistics, separated by mode, for a given user from the database.
    """
    query = select(Statistics)
    statistics = db.scalars(query).all()

    # for s in statistics:
    #     print(s, s.userID, s.mode)


    grouped = {}
    for stat in statistics:
        grouped.setdefault(stat.userID, {})[stat.mode] = stat

    return grouped