# app/vectorstore/base.py
from typing import List, Optional, Dict
from abc import ABC, abstractmethod
from ..db.schemas import ChunkDocument


class BaseVectorStore(ABC):
    """Abstract base class for all vector stores."""

    @abstractmethod
    def add_document(self, document: ChunkDocument) -> str:
        """
        Add a single document (chunk) to the vector store.
        Returns the inserted document's chunk_id.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[ChunkDocument]) -> List[str]:
        """
        Add multiple documents (chunks) to the vector store.
        Returns list of inserted chunk_ids.
        """
        pass

    @abstractmethod
    def search(
        self, query: str, top_k: int = 5, filters: Optional[Dict[str, str]] = None
    ):
        """
        Search for the most relevant documents.
        Returns list of (document, score).
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Delete documents from the vector store by chunk_ids."""
        pass
