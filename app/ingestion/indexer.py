import logging
import os
from datetime import datetime, timezone
from typing import List

from app.config.logging_config import setup_logging
from app.db import crud
from app.db.schemas import ChunkDocument, ChunkMetadata
from app.db.session import SessionLocal
from app.ingestion.hashing import Hasher
from app.ingestion.parser import base
from app.ingestion.parser.java_parser import JavaParser
from app.vectorstore.chroma import ChromaVectorStore
from app.ingestion.data_providers import ProjectDataProvider, LocalDataProvider, GitLabDataProvider


setup_logging()
logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self, vectorstore: ChromaVectorStore):
        self.vectorstore = vectorstore
        self.hasher = Hasher()
        self.parsers = {"java": JavaParser()}
        logger.info("Indexer initialized with vectorstore and parsers.")

    def _get_data_provider(self, project_path: str, branch: str = None) -> ProjectDataProvider:
        logger.info(f"Selecting data provider for path: {project_path}")
        if project_path.startswith(("http", "git@")):
            logger.info(f"Using GitLabDataProvider for {project_path} on branch {branch}")
            return GitLabDataProvider(repo_url=project_path, branch=branch)
        elif os.path.isdir(project_path):
            logger.info(f"Using LocalDataProvider for local path: {project_path}")
            return LocalDataProvider(project_path=project_path)
        else:
            logger.error(f"Invalid project path or URL: {project_path}")
            raise ValueError(f"Invalid project path or URL: {project_path}")

    def index_project(self, project_path: str, branch: str = None):
        logger.info(f"Starting full indexing for project: {project_path}")
        self._index_repo(project_path, branch, full_index=True)

    def reindex_project(self, project_path: str, branch: str = None):
        logger.info(f"Starting incremental reindexing for project: {project_path}")
        self._index_repo(project_path, branch, full_index=False)

    def _index_repo(self, project_path: str, branch: str = None, full_index: bool = False):
        db = SessionLocal()
        try:
            if full_index:
                repo = crud.create_repo(db, project_path, branch)
                logger.info(f"Created new repository record: {repo.url} (ID: {repo.id})")
            else:
                repo = crud.get_repo_by_url(db, project_path)
                if not repo:
                    logger.error(f"Cannot reindex non-existent repo: {project_path}")
                    raise ValueError(f"Cannot reindex non-existent repo: {project_path}")
                logger.info(f"Reindexing existing repository: {repo.url} (ID: {repo.id})")

            repo_id = repo.id
            provider = self._get_data_provider(project_path, branch)
            files = provider.list_files()
            logger.info(f"Found {len(files)} files to process in repo '{project_path}'")

            for file_path in files:
                logger.debug(f"Processing file: {file_path}")
                content = provider.get_file_content(file_path)
                prev_hash = crud.get_file_hash(db, repo, file_path)

                if not full_index and prev_hash and not self.hasher.has_changed(content, prev_hash):
                    logger.info(f"Skipping unchanged file: {file_path}")
                    continue

                parser = self._get_parser(file_path)
                chunks = self._parse_file(file_path, content, repo_id, parser)

                if chunks:
                    self._embed_and_store_chunks(chunks)
                    logger.info(f"Processed and embedded {len(chunks)} chunks for file: {file_path}")
                else:
                    logger.warning(f"No chunks extracted for file: {file_path}")

                new_hash = self.hasher.compute_hash(content)
                crud.update_file_hash(db, repo_id, file_path, new_hash)
                logger.debug(f"Updated hash for file: {file_path} -> {new_hash}")

            db.commit()
            logger.info(f"Completed {'full' if full_index else 'incremental'} indexing for repo: {project_path}")

        except Exception as e:
            logger.exception(f"Indexing failed for repo: {project_path} - {str(e)}")
            raise
        finally:
            db.close()
            logger.info("Database session closed.")

    def _get_parser(self, file_path: str) -> base.BaseParser:
        ext = file_path.split(".")[-1]
        parser = self.parsers.get(ext)
        if parser:
            logger.debug(f"Using parser '{parser.__class__.__name__}' for file: {file_path}")
        else:
            logger.debug(f"No parser found for file extension '{ext}'; using default chunking")
        return parser

    def _parse_file(self, file_path: str, content: str, repo_id: int, parser: base.BaseParser):
        chunks = []
        if parser:
            logger.debug(f"Parsing file {file_path} with {parser.__class__.__name__}")
            ast = parser.parse_file(content=content)
            chunks = parser.extract_chunks(ast, content, str(repo_id), file_path)
        else:
            chunk_id = self.hasher.compute_hash(f"{repo_id}:{file_path}")
            file_ext = file_path.split(".")[-1]
            chunks.append(
                ChunkDocument(
                    content=content,
                    metadata=ChunkMetadata(
                        chunk_id=chunk_id,
                        file_id=file_path,
                        repo_id=str(repo_id),
                        start_line=1,
                        end_line=content.count("\n") + 1,
                        language=file_ext,
                        author=None,
                        last_modified=datetime.now(timezone.utc).isoformat(),
                        class_context=None,
                    ),
                )
            )
            logger.debug(f"Created single default chunk for file: {file_path}")
        return chunks

    def _embed_and_store_chunks(self, chunks: List[ChunkDocument]):
        if chunks:
            logger.debug(f"Embedding {len(chunks)} chunks into vectorstore")
            self.vectorstore.add_documents(chunks)
            logger.info(f"Successfully added {len(chunks)} chunks to vectorstore")
        else:
            logger.warning("No chunks to embed into vectorstore")
