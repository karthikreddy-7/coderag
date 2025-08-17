# app/db/schemas.py
"""
Pydantic Schemas:
- Define request/response models for API
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from pathlib import Path

class ChunkMetadata(BaseModel):
    """
    Metadata schema for a single chunk of code/text.
    This acts as a DTO (Data Transfer Object) across the project.
    """
    chunk_id: str
    file_id: str
    repo_id: str
    start_line: int
    end_line: int
    language: Optional[str] = None
    author: Optional[str] = None
    last_modified: Optional[datetime] = None

class ChunkDocument(BaseModel):
    """
    Document schema that wraps content with its metadata.
    """
    content: str
    metadata: ChunkMetadata

# ---------------- Repo ----------------
class RepoBase(BaseModel):
    name: str
    url: str
    branch: Optional[str] = "main"


class RepoCreate(RepoBase):
    pass


class RepoRead(RepoBase):
    id: int
    created_at: datetime



# ---------------- FileChunk ----------------
class FileChunkBase(BaseModel):
    repo_id: int
    file_path: str
    start_line: int
    end_line: int
    content: str
    hash: str


class FileChunkCreate(FileChunkBase):
    pass


class FileChunkRead(FileChunkBase):
    id: int
    created_at: datetime



# ---------------- EmbeddingIndex ----------------
class EmbeddingBase(BaseModel):
    chunk_id: int
    vectorstore_id: str


class EmbeddingCreate(EmbeddingBase):
    pass


class EmbeddingRead(EmbeddingBase):
    id: int

