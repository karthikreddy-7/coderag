from typing import Optional, List
from sqlalchemy.orm import Session
from . import models

# ------------------- Repo -------------------
def get_repo(db: Session, repo_url: str) -> Optional[models.Repo]:
    return db.query(models.Repo).filter(models.Repo.url == repo_url).first()

def get_repo_by_id(db: Session, repo_id: str) -> Optional[models.Repo]:
    return db.query(models.Repo).filter(models.Repo.id == repo_id).first()

def create_repo(db: Session, project_path: str, branch: str) -> models.Repo:
    repo_name = project_path.rstrip("/").split("/")[-1]
    repo = models.Repo(name=repo_name, url=project_path, branch=branch or "main")
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo

def list_repos(db: Session) -> List[models.Repo]:
    return db.query(models.Repo).all()

def delete_repo(db: Session, repo_url: str):
    repo = get_repo(db, repo_url)
    if repo:
        db.delete(repo)
        db.commit()

# ------------------- File & Hash -------------------
def get_file(db: Session, repo_id: int, file_path: str) -> Optional[models.File]:
    return db.query(models.File).filter(models.File.repo_id == repo_id, models.File.path == file_path).first()

def get_file_hash(db: Session, repo, file_path: str) -> Optional[str]:
    file = get_file(db, repo.id, file_path)
    return file.hash if file else None

def update_file_hash(db: Session, repo_id: int, file_path: str, new_hash: str):
    file = get_file(db, repo_id, file_path)
    if file:
        file.hash = new_hash
    else:
        file = models.File(repo_id=repo_id, path=file_path, hash=new_hash)
        db.add(file)
