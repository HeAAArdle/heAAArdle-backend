from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Kakatamad i-satisfy si Pylance idgaf nalang
engine = create_engine(settings.database_url) # type: ignore

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()