from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.ingestion.indexer import Indexer
from app.db import crud, session
from app.vectorstore.chroma import ChromaVectorStore

router = APIRouter(prefix="/repos", tags=["Repositories"])

# Initialize vector store and indexer
vectorstore = ChromaVectorStore()
indexer = Indexer(vectorstore)


class RepoCreateRequest(BaseModel):
    project_path: str
    branch: Optional[str] = None


@router.post("/")
def add_or_reindex_repo(request: RepoCreateRequest, db: Session = Depends(session.get_db)):
    """Add a new repository or reindex an existing one."""
    repo = crud.get_repo(db, request.project_path)
    if repo:
        try:
            indexer.reindex_project(repo.url, repo.branch)
            return {"message": "Repository reindexed successfully", "repo_id": repo.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")
    else:
        try:
            indexer.index_project(request.project_path, request.branch)
            # Fetch the newly created repo record to return its ID
            new_repo = crud.get_or_create_repo(db, request.project_path, request.branch)
            return {"message": "Repository added and indexed successfully", "repo_id": new_repo.id}
        except Exception as e:
            crud.delete_repo(db, request.project_path)
            raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.get("/")
def list_repos():
    """List all repos stored in DB."""
    repos = crud.list_repos(session)
    return {"repos": repos}
