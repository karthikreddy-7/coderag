import os
from datetime import datetime, timezone
from typing import List

from app.db import crud
from app.db.schemas import ChunkDocument, ChunkMetadata
from app.db.session import SessionLocal
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
        # Create a single session for this indexing operation
        db = SessionLocal()
        try:
            if full_index:
                # New repo, create if not exists
                repo = crud.create_repo(db, project_path, branch)
                print("Creating a new repository")
            else:
                # Reindexing: fetch existing repo
                repo = crud.get_repo(db, project_path)
                print("Fetched and re-indexing old repository")
                if not repo:
                    raise ValueError(f"Cannot reindex. Repo {project_path} does not exist.")
            repo_id = repo.id
            # Get the correct data provider
            data_provider = self._get_data_provider(project_path, branch)
            files = data_provider.list_files()
            for file_path in files:
                content = data_provider.get_file_content(file_path)
                # Get previous hash if exists
                prev_hash = crud.get_file_hash(db, repo, file_path)
                # Skip unchanged files in incremental reindex
                if not full_index and prev_hash and not self.hasher.has_changed(content, prev_hash):
                    continue
                # Determine parser
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
                    chunk_id = self.hasher.compute_hash(f"{repo_id}:{file_path}")
                    chunk = ChunkDocument(
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
                            class_context=None
                        )
                    )
                    chunks.append(chunk)

                # Embed and store chunks in vector store
                if chunks:
                    self._embed_and_store_chunks(chunks)

                # Update file hash in DB
                crud.update_file_hash(db, repo_id, file_path, self.hasher.compute_hash(content))

            db.commit()

        finally:
            # Ensure the session is closed, even if errors occur
            db.close()

    def _get_parser(self, file_path: str) -> base.BaseParser:
        """Return parser based on file extension."""
        ext = file_path.split(".")[-1]
        return self.parsers.get(ext)

    def _embed_and_store_chunks(self, chunks: List[ChunkDocument]):
        """Embeds and stores chunks ONLY in the vector store."""
        if not chunks:
            return
        self.vectorstore.add_documents(chunks)

"""
if __name__ == "__main__":
    import sys
    from app.vectorstore.chroma import ChromaVectorStore

    # Provide the path to your local project here
    project_path = "/home/karthik/dev/CraftMyCV/backend"  # <- change this to your local repo

    # Initialize vector store (you can configure path/persist if needed)
    vectorstore = ChromaVectorStore(persist_directory="./vectorstore_test")

    # Initialize the indexer
    indexer = Indexer(vectorstore=vectorstore)

    # Perform full indexing
    print(f"Indexing project at: {project_path}")
    indexer.index_project(project_path)
    print("Indexing completed!")
"""
