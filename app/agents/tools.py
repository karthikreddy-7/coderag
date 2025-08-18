from __future__ import annotations

import logging
from typing import Dict, List, Any

from app.retrieval.retriever import Retriever
from app.vectorstore.chroma import ChromaVectorStore
from app.db import crud
from app.ingestion.data_providers import LocalDataProvider, GitLabDataProvider

logger = logging.getLogger(__name__)


class AgentTools:
    """
    Wraps concrete tool functions the agent can call.
    Kept simple (direct callables) so we don't need runtime tool-binding magic.
    """
    def __init__(self, db, vectorstore: ChromaVectorStore):
        self.db = db
        self.vectorstore = vectorstore
        self.retriever = Retriever(vectorstore=vectorstore)

    def get_tools(self) -> Dict[str, callable]:
        def get_more_context(*, query: str, repo_id: str, top_k: int = 5) -> str:
            """
            Semantic retrieval over the indexed chunks for a given repo.
            Returns stitched snippets with file hints.
            """
            logger.info(f"Tool 'get_more_context' called with query: '{query}' for repo_id: {repo_id}")
            try:
                repo_id_int = int(repo_id)
            except (ValueError, TypeError):
                return f"Error: Invalid repo_id '{repo_id}'. Must be an integer."
            results: List[Dict[str, Any]] = self.retriever.get_formatted_context(
                query=query,
                top_k=top_k,
                repo_id=repo_id_int
            )
            if not results:
                return "No relevant context found in the repository."
            # Format the results into a single string
            stitched_context = ""
            for i, result in enumerate(results):
                metadata = result.get("metadata", {})
                file_path = metadata.get("file_id", "Unknown file")
                content = result.get("content", "No content")
                stitched_context += f"--- Snippet {i + 1} from file: {file_path} ---\n"
                stitched_context += f"{content}\n\n"

            logger.info(f"Returning {len(results)} stitched snippets for the query.")
            return stitched_context.strip()

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


if __name__ == '__main__':
    # This block allows for direct testing of the tools.
    # Note: You must have an indexed repository in your DB and VectorStore.

    # 1. Setup basic logging to see the output
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    # 2. Import necessary components for initialization
    from app.db.session import SessionLocal
    from app.vectorstore.chroma import ChromaVectorStore

    # 3. Initialize database and vector store
    db_session = SessionLocal()
    vector_store = ChromaVectorStore()

    # 4. Create an instance of AgentTools
    agent_tools_instance = AgentTools(db=db_session, vectorstore=vector_store)
    tools = agent_tools_instance.get_tools()

    # --- Test Case 1: Get More Context ---
    print("\n--- Testing 'get_more_context' tool ---")
    # Replace '1' with a valid repo_id from your database
    TEST_REPO_ID = "1"
    context_query = "How is the UserProfile controller implemented?"
    context_result = tools["get_more_context"](query=context_query, repo_id=TEST_REPO_ID, top_k=2)
    print(f"Query: {context_query}\nResult:\n{context_result}")

    # --- Test Case 2: Get Specific File ---
    print("\n\n--- Testing 'get_specific_file' tool ---")
    # Replace with a valid file_path from the repo corresponding to TEST_REPO_ID
    TEST_FILE_PATH = "src/main/java/com/karthik/resume/backend/service/impl/UserProfileServiceImpl.java"
    file_content_result = tools["get_specific_file"](file_path=TEST_FILE_PATH, repo_id=TEST_REPO_ID)
    print(f"File Path: {TEST_FILE_PATH}\nResult:\n{file_content_result}")  # Print first 500 chars

    # 5. Close the database session
    db_session.close()