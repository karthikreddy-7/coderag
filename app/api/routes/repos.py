# app/api/routes/repos.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ingestion.indexer import Indexer
from app.db import crud, session
from app.vectorstore.chroma import ChromaVectorStore

router = APIRouter(prefix="/repos")

# Initialize vector store and indexer
vectorstore = ChromaVectorStore()
indexer = Indexer(vectorstore)


class RepoCreateRequest(BaseModel):
    repo_url: str
    branch: str = "main"


@router.post("/")
def add_or_reindex_repo(request: RepoCreateRequest):
    """
    Add a new repository or reindex an existing one.
    - If repo exists: perform incremental reindex.
    - If repo doesn't exist: add and perform full index.
    """
    existing_repo = crud.get_repo_by_id(session, request.repo_url)

    if existing_repo:
        # Repo exists → perform reindex
        try:
            indexer.reindex_project(request.repo_url, request.branch)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")
        return {"message": "Repository reindexed successfully", "repo_id": existing_repo.id}

    # Repo doesn't exist → add and full index
    repo_record = crud.create_repo(session, request.repo_url, request.branch)
    try:
        indexer.index_project(request.repo_url, request.branch)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

    return {"message": "Repository added and indexed successfully", "repo_id": repo_record.id}


@router.get("/")
def list_repos():
    """List all repos stored in DB."""
    repos = crud.list_repos(session)
    return {"repos": repos}
