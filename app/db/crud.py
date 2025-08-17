from typing import Optional
from sqlalchemy.orm import Session
from . import models

def get_repo(db: Session, repo_url: str) -> Optional[models.Repo]:
    """Get a repository by its URL."""
    return db.query(models.Repo).filter(models.Repo.url == repo_url).first()

def get_or_create_repo(db: Session, repo_url: str, branch: str) -> models.Repo:
    """Get a repository by its URL, or create it if it doesn't exist."""
    repo = get_repo(db, repo_url)
    if not repo:
        repo = models.Repo(name=repo_url, url=repo_url, branch=branch or "main")
        db.add(repo)
        db.commit()
    return repo

def get_file(db: Session, repo_id: int, file_path: str) -> Optional[models.File]:
    """Get a file by its repository ID and path."""
    return db.query(models.File).filter(models.File.repo_id == repo_id, models.File.path == file_path).first()

def get_file_hash(db: Session, repo_url: str, file_path: str) -> Optional[str]:
    """Get the stored hash for a specific file in a repository."""
    repo = get_repo(db, repo_url)
    file = get_file(db, repo.id, file_path)
    return file.hash if file else None

def update_file_hash(db: Session, repo_url: str, file_path: str, new_hash: str):
    """Update or create a file record with its new content hash."""
    repo = get_or_create_repo(db, repo_url, branch="main")
    file = get_file(db, repo.id, file_path)
    if file:
        file.hash = new_hash
    else:
        file = models.File(repo_id=repo.id, path=file_path, hash=new_hash)
        db.add(file)