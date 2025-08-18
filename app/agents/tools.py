# app/agents/tools.py
from __future__ import annotations

from typing import Dict

from app.vectorstore.chroma import ChromaVectorStore
from app.db import crud
from app.ingestion.data_providers import LocalDataProvider, GitLabDataProvider


class AgentTools:
    """
    Wraps concrete tool functions the agent can call.
    Kept simple (direct callables) so we don't need runtime tool-binding magic.
    """

    def __init__(self, db, vectorstore: ChromaVectorStore):
        self.db = db
        self.vectorstore = vectorstore

    def get_tools(self) -> Dict[str, callable]:
        def get_more_context(*, query: str, repo_id: str, top_k: int = 5) -> str:
            """
            Semantic retrieval over the indexed chunks for a given repo.
            Returns stitched snippets with file hints.
            """
            print("Inside get_more_context")
            repo = crud.get_repo_by_id(self.db, repo_id)
            results = self.vectorstore.search(
                query=query,
                top_k=top_k,
                filter={"repo_id": str(repo.id)},
            )

            if not results:
                return "No relevant context found."

            stitched = []
            for doc in results:
                file_id = doc.metadata.get("file_id") or doc.metadata.get("path") or "unknown"
                stitched.append(f"--- File: {file_id} ---\n{doc.page_content}")
            return "\n\n".join(stitched)

        def get_specific_file(*, file_path: str, repo_id: str) -> str:
            """
            Fetch the raw contents of a concrete file path from the repo source (local or Git remote).
            """
            repo = crud.get_repo_by_id(self.db, repo_id)
            provider = (
                GitLabDataProvider(repo.url)
                if isinstance(repo.url, str) and repo.url.startswith("http")
                else LocalDataProvider(repo.url)
            )
            try:
                return provider.get_file_content(file_path)
            except Exception as e:
                return f"Error fetching file '{file_path}': {e}"

        # Expose as a dict for explicit access
        return {
            "get_more_context": get_more_context,
            "get_specific_file": get_specific_file,
        }
