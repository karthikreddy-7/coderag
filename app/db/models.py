# app/db/models.py
"""
Database Models:
- Repo, File, Chunk
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Repo(Base):
    """Repository tracked by the system."""
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String, nullable=True)
    branch = Column(String, default="main")
    last_indexed = Column(DateTime, default=datetime.utcnow)

    files = relationship("File", back_populates="repo", cascade="all, delete-orphan")


class File(Base):
    """Represents a file in a repository."""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id", ondelete="CASCADE"))
    path = Column(String, index=True)
    hash = Column(String, index=True)  # track changes

    repo = relationship("Repo", back_populates="files")
