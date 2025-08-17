# app/api/routes/queries.py
"""
Query Routes:
- Accept user queries
- Route them to MasterAgent
"""

from fastapi import APIRouter

router = APIRouter(prefix="/queries")

@router.post("/")
def process_query(query: str):
    """Submit a query for processing by agents."""
    pass
