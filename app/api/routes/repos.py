from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from app.ingestion.indexer import Indexer
from app.db import crud, session
from app.vectorstore.chroma import ChromaVectorStore
from app.config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repos", tags=["Repositories"])
vectorstore = ChromaVectorStore()
indexer = Indexer(vectorstore)

class RepoCreateRequest(BaseModel):
    project_path: str
    branch: str | None = None

@router.post("/")
def add_or_reindex_repo(request: RepoCreateRequest, db: Session = Depends(session.get_db)):
    repo = crud.get_repo_by_url(db, request.project_path)
    try:
        if repo:
            logger.info(f"Reindexing repository: {request.project_path}")
            indexer.reindex_project(repo.url, repo.branch)
            return {"message": "Repository reindexed successfully", "repo_id": repo.id}
        else:
            logger.info(f"Adding and indexing new repository: {request.project_path}")
            indexer.index_project(request.project_path, request.branch)
            new_repo = crud.get_repo_by_url(db, request.project_path)
            return {"message": "Repository added and indexed successfully", "repo_id": new_repo.id}
    except Exception as e:
        logger.error(f"Indexing failed for {request.project_path}: {str(e)}")
        if not repo:
            crud.delete_repo(db, request.project_path)
            logger.info(f"Deleted partially indexed repository: {request.project_path}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@router.get("/")
def list_repos(db: Session = Depends(session.get_db)):
    repos = crud.list_repos(db)
    logger.info(f"Listing all repositories, count: {len(repos)}")
    return {"repos": repos}
