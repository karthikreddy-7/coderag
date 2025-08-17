# app/db/session.py
"""
Database Session:
- SQLAlchemy session setup for SQLite
"""

# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./coderag.db"  # local SQLite DB

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # required for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
