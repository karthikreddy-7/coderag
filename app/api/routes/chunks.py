# app/api/routes/chunks.py
"""
Chunk Routes:
- Expose API for inspecting indexed chunks
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.vectorstore.chroma import ChromaVectorStore
from app.db import session

router = APIRouter(prefix="/chunks", tags=["Chunks"])
vectorstore = ChromaVectorStore()

@router.get("/{repo_url}")
def list_chunks_for_repo(repo_url: str):
    """List all chunks indexed for a repository by its URL."""
    results = vectorstore.vectorstore.get(where={"repo_id": repo_url})
    return {"count": len(results.get('ids', [])), "chunks": results}
