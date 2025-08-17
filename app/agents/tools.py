# app/agents/tools.py
"""
Agent Tools:
- Provides helper methods like:
    - get_more_context(query)
    - get_specific_file(path)
- Tools are invoked by CodeRAGAgent
"""

from sqlalchemy.orm import Session
from app.vectorstore.chroma import ChromaVectorStore
from app.db import crud
from app.ingestion.data_providers import LocalDataProvider, GitLabDataProvider


class AgentTools:
    def __init__(self, db: Session, vectorstore: ChromaVectorStore):
        self.db = db
        self.vectorstore = vectorstore

    def get_more_context(self, query: str, repo_id: str) -> str:
        """Retrieve relevant code chunks for a query from the vector store."""
        repo = crud.get_repo(self.db, repo_id)
        # Filter search by the specific repository
        search_results = self.vectorstore.search(query, top_k=5, filters={"repo_id": repo.url})

        context_str = ""
        for doc in search_results:
            context_str += f"--- File: {doc.metadata.get('file_id', 'N/A')} ---\n"
            context_str += doc.page_content
            context_str += "\n--------------------------------------------------\n"
        return context_str

    def get_specific_file(self, file_path: str, repo_id: str) -> str:
        """Fetch raw code file content by its path within a repo."""
        repo = crud.get_repo(self.db, repo_id)
        # Use data providers to get file content
        if repo.url.startswith("http"):
            provider = GitLabDataProvider(repo_url=repo.url)
        else:
            provider = LocalDataProvider(project_path=repo.url)

        try:
            content = provider.get_file_content(file_path)
            return content
        except Exception as e:
            return f"Error: Could not retrieve file '{file_path}'. Reason: {e}"
