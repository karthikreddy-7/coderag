# app/api/routes/queries.py
"""
Query Routes:
- Accept user queries
- Route them to MasterAgent
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import session
from app.agents.master_agent import MasterAgent
from app.agents.tools import AgentTools
from app.vectorstore.chroma import ChromaVectorStore

router = APIRouter(prefix="/query", tags=["Queries"])

vectorstore = ChromaVectorStore()


class QueryRequest(BaseModel):
    repo_id: int
    query: str


@router.post("/")
def process_query(request: QueryRequest, db: Session = Depends(session.get_db)):
    """Submit a query to a specific repository."""
    tools = AgentTools(db=db, vectorstore=vectorstore)
    master_agent = MasterAgent(tools=tools)

    answer = master_agent.handle_query(query=request.query, repo_id=request.repo_id)
    return {"answer": answer}
