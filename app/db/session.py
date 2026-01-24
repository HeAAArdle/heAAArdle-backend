from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from app.core.config import settings

assert settings.database_url is not None, "Missing database URL in .env."

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
