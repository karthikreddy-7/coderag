import os
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from app.db import crud
from app.db.schemas import ChunkDocument, ChunkMetadata
from app.ingestion.hashing import Hasher
from app.ingestion.parser import base
from app.ingestion.parser.java_parser import JavaParser
from app.vectorstore.chroma import ChromaVectorStore
from app.ingestion.data_providers import ProjectDataProvider, LocalDataProvider, GitLabDataProvider


"""
Indexer Module
Orchestrates the full ingestion pipeline for a repository:
1. Parsing files via language-specific parsers.
2. Chunking parsed files into logical sections.
3. Computing file hashes and detecting changes.
4. Embedding chunks and updating the vector store.
5. Storing/updating metadata in the relational database.

Acts as the main entry point for repository indexing.
"""


class Indexer:
    def __init__(self, vectorstore: ChromaVectorStore):
        self.vectorstore = vectorstore
        self.hasher = Hasher()
        self.parsers = {
            "java": JavaParser(),
        }

    def _get_data_provider(self, project_path: str, branch: str = None) -> ProjectDataProvider:
        """Factory method to create the correct data provider."""
        if project_path.startswith("http") or project_path.startswith("git@"):
            return GitLabDataProvider(repo_url=project_path, branch=branch)
        elif os.path.isdir(project_path):
            return LocalDataProvider(project_path=project_path)
        else:
            raise ValueError(f"Invalid project path or URL: {project_path}")

    def index_project(self, project_path: str, branch: str = None):
        """Full indexing for a new repository or local path."""
        self._index_repo(project_path, branch, full_index=True)

    def reindex_project(self, project_path: str, branch: str = None):
        """Incremental reindex for an existing repository or local path."""
        self._index_repo(project_path, branch, full_index=False)

    def _index_repo(self, project_path: str, branch: str = None, full_index: bool = False):
        """Core indexing logic for both parsable and non-parsable files."""
        repo_id = project_path
        data_provider = self._get_data_provider(project_path, branch)
        files = data_provider.list_files()

        for file_path in files:
            content = data_provider.get_file_content(file_path)
            prev_hash = crud.get_file_hash(repo_id, file_path)

            if not full_index and not self.hasher.has_changed(content, prev_hash):
                continue

            parser = self._get_parser(file_path)
            chunks = []

            if parser:
                # If a specific parser exists, use it to extract detailed chunks.
                print(f"Parsing {file_path} with {parser.__class__.__name__}...")
                ast = parser.parse_file(content=content)
                chunks = parser.extract_chunks(ast, content, repo_id, file_path)
            else:
                # If no parser exists, treat the whole file as a single chunk.
                print(f"No parser for {file_path}. Treating as a single chunk.")
                file_ext = file_path.split(".")[-1]
                chunk = ChunkDocument(
                    content=content,
                    metadata=ChunkMetadata(
                        chunk_id=str(uuid4()),
                        file_id=file_path,
                        repo_id=repo_id,
                        start_line=1,
                        end_line=content.count('\n') + 1,
                        language=file_ext,
                        author=None,
                        last_modified=datetime.now(timezone.utc),
                        class_context=None
                    )
                )
                chunks.append(chunk)

            if chunks:
                self._embed_and_store_chunks(chunks)
                crud.update_file_hash(repo_id, file_path, self.hasher.compute_hash(content))

    def _get_parser(self, file_path: str) -> base.BaseParser:
        """Return parser based on file extension."""
        ext = file_path.split(".")[-1]
        return self.parsers.get(ext)

    def _embed_and_store_chunks(self, chunks: List[ChunkDocument]):
        for chunk in chunks:
            self.vectorstore.upsert(
                vector_id=chunk.metadata.chunk_id,
                metadata=chunk.metadata.model_dump()
            )
            crud.save_chunk_metadata(chunk.metadata)