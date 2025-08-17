# app/db/session.py
"""
Database Session:
- SQLAlchemy session setup for SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./coderag.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
