# app/api/routes/queries.py
"""
Query Routes:
- Accept user queries
- Route them to CoderagAgent (Agentic-RAG loop: decide → retrieve → grade → rewrite? → answer)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import session
from app.vectorstore.chroma import ChromaVectorStore
from app.agents.tools import AgentTools
from app.agents.coderag_agent import CoderagAgent

router = APIRouter(prefix="/query", tags=["Queries"])

vectorstore = ChromaVectorStore()


class QueryRequest(BaseModel):
    repo_id: int = Field(..., description="Internal repository ID")
    query: str = Field(..., min_length=2, description="User question")


@router.post("/", summary="Process a query against a repository")
def process_query(request: QueryRequest, db: Session = Depends(session.get_db)):
    """
    Submit a query to a specific repository. Returns an Agentic-RAG structured result.
    """
    tools = AgentTools(db=db, vectorstore=vectorstore)
    agent = CoderagAgent(tools=tools)

    result = agent.handle_query(query=request.query, repo_id=request.repo_id)
    return result
