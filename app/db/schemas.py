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

    @field_validator("file_path")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        """Ensure file paths are stored in a normalized form (POSIX style)."""
        return str(Path(v).as_posix())

    @field_validator("end_line")
    @classmethod
    def check_line_numbers(cls, v: int, values) -> int:
        """Ensure end_line is not before start_line."""
        if "start_line" in values and v < values["start_line"]:
            raise ValueError("end_line cannot be smaller than start_line")
        return v

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

    class Config:
        orm_mode = True


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

    class Config:
        orm_mode = True


# ---------------- EmbeddingIndex ----------------
class EmbeddingBase(BaseModel):
    chunk_id: int
    vectorstore_id: str


class EmbeddingCreate(EmbeddingBase):
    pass


class EmbeddingRead(EmbeddingBase):
    id: int

    class Config:
        orm_mode = True

