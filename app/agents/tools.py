# app/agents/tools.py

from langchain_core.tools import tool
from app.vectorstore.chroma import ChromaVectorStore
from app.db import crud
from app.ingestion.data_providers import LocalDataProvider, GitLabDataProvider

class AgentTools:
    def __init__(self, db, vectorstore: ChromaVectorStore):
        self.db = db
        self.vectorstore = vectorstore

    def get_tools(self):
        @tool
        def get_more_context(query: str, repo_id: str, top_k: int = 5) -> str:
            """
            Retrieve relevant code context from a repository using a query.
            Defaults to 'default_repo' if repo_id is not provided.
            """
            repo = crud.get_repo_by_id(self.db, repo_id)
            search_results = self.vectorstore.search(
                query, top_k=top_k, filters={"repo_id": repo.id}
            )
            if not search_results:
                return "No relevant context found."
            return "\n".join(
                f"--- File: {doc.metadata.get('file_id', 'N/A')} ---\n{doc.page_content}"
                for doc in search_results
            )

        @tool
        def get_specific_file(file_path: str, repo_id: str) -> str:
            """
            Retrieve relevant code context from a repository using a query.
            repo_id: the internal ID of the repo in the database
            top_k: number of results to return
            """
            repo = crud.get_repo_by_id(self.db, repo_id)
            provider = GitLabDataProvider(repo.url) if repo.url.startswith("http") else LocalDataProvider(repo.url)
            try:
                return provider.get_file_content(file_path)
            except Exception as e:
                return f"Error fetching file: {e}"

        return [get_more_context, get_specific_file]

