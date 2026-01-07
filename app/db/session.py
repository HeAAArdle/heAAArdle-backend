from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Kakatamad i-satisfy si Pylance idgaf nalang
engine = create_engine(settings.database_url)
 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)