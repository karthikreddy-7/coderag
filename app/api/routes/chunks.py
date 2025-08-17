# app/api/routes/chunks.py
"""
Chunk Routes:
- Expose API for inspecting indexed chunks
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chunks")

@router.get("/{repo_id}")
def list_chunks(repo_id: int):
    """List all chunks indexed for a repository."""
    pass
