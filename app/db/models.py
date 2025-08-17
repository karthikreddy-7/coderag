# app/db/models.py
"""
Database Models:
- Repo, File, Chunk
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    branch = Column(String)

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer)
    path = Column(String)
    hash = Column(String)

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer)
    content = Column(String)
    embedding = Column(String)  # serialized vector
