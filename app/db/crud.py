from typing import Optional, List
from sqlalchemy.orm import Session
from . import models

def get_repo(db: Session, repo_url: str) -> Optional[models.Repo]:
    """Get a repository by its URL."""
    return db.query(models.Repo).filter(models.Repo.url == repo_url).first()

def create_repo(db: Session, project_path: str, branch: str) -> models.Repo:
    """Get a repository by its path, or create it if it doesn't exist."""
    print("creating a new repo ")
    repo_name = project_path.rstrip("/").split("/")[-1]
    repo = models.Repo(
        name=repo_name,
        url=project_path,
        branch=branch or "main"
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo

def get_file(db: Session, repo_id: int, file_path: str) -> Optional[models.File]:
    """Get a file by its repository ID and path."""
    return db.query(models.File).filter(models.File.repo_id == repo_id, models.File.path == file_path).first()

def get_file_hash(db: Session, repo, file_path: str) -> Optional[str]:
    """Get the stored hash for a specific file in a repository."""
    file = get_file(db, repo.id, file_path)
    return file.hash if file else None

def update_file_hash(db: Session, repo_url: str, file_path: str, new_hash: str):
    """Update or create a file record with its new content hash."""
    repo = get_repo(db, repo_url)
    file = get_file(db, repo.id, file_path)
    if file:
        file.hash = new_hash
    else:
        file = models.File(repo_id=repo.id, path=file_path, hash=new_hash)
        db.add(file)

def list_repos(db: Session) -> List[models.Repo]:
    """Return all repositories from the database."""
    return db.query(models.Repo).all()