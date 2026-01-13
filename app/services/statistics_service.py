from sqlalchemy.orm import Session
from app.models.statistics import Statistics

def get_db_statistics(db: Session, user_id: str) -> dict[str, Statistics]:
    stats = (db.query(Statistics).filter(Statistics.userID == user_id).all())
    return {stat.mode: stat for stat in stats}
