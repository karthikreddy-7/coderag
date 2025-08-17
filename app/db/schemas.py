# app/db/schemas.py
"""
Pydantic Schemas:
- Define request/response models for API
"""

from pydantic import BaseModel

class RepoCreate(BaseModel):
    url: str
    branch: str

class RepoOut(BaseModel):
    id: int
    url: str
    branch: str
