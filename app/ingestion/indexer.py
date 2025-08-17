# app/ingestion/indexer.py
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
    def index_repo(self, repo_path: str):
        """Index repo into chunks + embeddings."""
        pass
