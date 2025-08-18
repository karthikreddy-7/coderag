import logging
from typing import List, Dict, Any, Optional

from langchain_core.documents import Document

from app.vectorstore.base import BaseVectorStore
from app.vectorstore.chroma import ChromaVectorStore

# Configure logging
logger = logging.getLogger(__name__)


class Retriever:
    """
    Handles retrieving context, metadata, and documents from a vector store.
    It provides a high-level API for searching and fetching indexed data.
    """

    def __init__(self, vectorstore: BaseVectorStore):
        """
        Initializes the Retriever with a vector store instance.

        Args:
            vectorstore: An instance of a class that inherits from BaseVectorStore,
                         such as ChromaVectorStore.
        """
        self.vectorstore = vectorstore
        logger.info(f"Retriever initialized with {type(vectorstore).__name__}.")

    def retrieve_context(
            self, query: str, top_k: int = 5, repo_id: Optional[int] = None
    ) -> List[Document]:
        """
        Performs a similarity search on the vector store to find relevant documents.

        Args:
            query: The text query to search for.
            top_k: The number of top results to return.
            repo_id: The optional ID of the repository to filter the search by.

        Returns:
            A list of LangChain Document objects, which include content and metadata.
        """
        filters = {}
        if repo_id:
            filters["repo_id"] = str(repo_id)  # ChromaDB filter values must be strings

        logger.info(f"Retrieving top {top_k} documents for query: '{query[:60]}...' with filters: {filters}")
        try:
            results = self.vectorstore.search(query, top_k=top_k, filter=filters if filters else None)
            logger.info(f"Found {len(results)} relevant documents.")
            return results
        except Exception as e:
            logger.error(f"An error occurred during context retrieval: {e}")
            return []

    def get_formatted_context(
            self, query: str, top_k: int = 5, repo_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves context and formats it into a more universally usable
        list of dictionaries.
        Args:
            query: The text query to search for.
            top_k: The number of top results to return.
            repo_id: The optional ID of the repository to filter the search by.

        Returns:
            A list of dictionaries, where each dictionary contains the 'content'
            and 'metadata' of a retrieved chunk.
        """
        documents = self.retrieve_context(query, top_k, repo_id)
        formatted_results = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in documents
        ]
        return formatted_results

# Example of how to use the Retriever class
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    # 1. Initialize the vector store and the retriever
    chroma_vs = ChromaVectorStore()
    retriever = Retriever(vectorstore=chroma_vs)
    # 2. Define a query
    search_query = "How are user profiles managed in the controller?"
    # 3. Use the retriever to get formatted context
    print("\n--- Testing get_formatted_context ---")
    formatted_context = retriever.get_formatted_context(query=search_query, top_k=3,repo_id=1)
    if formatted_context:
        for i, item in enumerate(formatted_context):
            print(f"\nResult {i + 1}:")
            print(f"  Metadata: {item['metadata']}")
            print(f"  Content: '{item['content']}...'")
    else:
        print("No results found.")