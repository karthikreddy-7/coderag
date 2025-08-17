from typing import List, Dict, Any

from app.db.schemas import ChunkDocument
from app.ingestion.hashing import Hasher
from app.ingestion.chunker import Chunker
from app.ingestion.parser import base
from app.db import crud
from app.ingestion.parser.java_parser import JavaParser
from app.vectorstore.chroma import ChromaVectorStore
from app.ingestion.git_utils import GitUtils


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
        self.chunker = Chunker()
        self.parsers = {
            "java": JavaParser(),
        }
        self.git_utils = GitUtils()

    def index_project(self, repo_url: str, branch: str = None):
        """Full indexing for a new repository."""
        self._index_repo(repo_url, branch, full_index=True)

    def reindex_project(self, repo_url: str, branch: str = None):
        """Incremental reindex for an existing repository."""
        self._index_repo(repo_url, branch, full_index=False)

    def _index_repo(self, repo_url: str, branch: str = None, full_index: bool = False):
        """Core indexing logic. Supports both full and incremental indexing."""
        branch = branch or self.git_utils._get_default_branch(repo_url)
        files = self.git_utils.list_files(repo_url, branch)

        for file_path in files:
            content = self.git_utils.get_file_content(repo_url, file_path, branch)
            prev_hash = crud.get_file_hash(repo_url, file_path)

            if not full_index and not self.hasher.has_changed(content, prev_hash):
                continue

            parser = self._get_parser(file_path)
            ast = parser.parse_file(content=content)
            chunks = parser.extract_chunks(ast)
            self._embed_and_store_chunks(repo_url, file_path, chunks)
            crud.update_file_hash(repo_url, file_path, self.hasher.compute_hash(content))

    def _get_parser(self, file_path: str) -> base.BaseParser:
        """Return parser based on file extension; fallback to JavaParser for now."""
        ext = file_path.split(".")[-1]
        return self.parsers.get(ext)

    def embed_and_store_chunks(self,chunks: List[ChunkDocument], vector_store, db_crud):
        for chunk in chunks:
            self.vectorstore.upsert(vector_id=chunk.metadata.chunk_id,metadata=chunk.metadata.model_dump())
            db_crud.save_chunk_metadata(chunk.metadata)

