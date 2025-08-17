# app/api/routes/repos.py
"""
Repository Routes:
- Register new repos
- Switch branches
- List repos linked with tool
"""

from fastapi import APIRouter

router = APIRouter(prefix="/repos")

@router.post("/")
def add_repo(repo_url: str):
    """Add and index a new repository."""
    pass

@router.get("/")
def list_repos():
    """List all repos stored in DB."""
    pass
