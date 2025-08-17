# app/vectorstore/chroma.py
from langchain.vectorstores import Chroma
from typing import List, Optional, Dict
from .base import BaseVectorStore
from ..db.schemas import ChunkMetadata, ChunkDocument
from ..ingestion.embedder import Embedder


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB implementation of vector store abstraction."""
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embedding_model = Embedder()
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embedding_model
        )

    def add_document(self, document: ChunkDocument) -> str:
        """Add a single document with metadata."""
        self.vectorstore.add_texts(
            texts=[document.content],
            metadatas=[document.metadata.model_dump()],
            ids=[document.metadata.chunk_id],
        )
        return document.metadata.chunk_id

    def add_documents(self, documents: List[ChunkDocument]) -> List[str]:
        """Add a list of documents in a single batch."""
        if not documents:
            return []
        ids = [doc.metadata.chunk_id for doc in documents]
        texts = [doc.content for doc in documents]
        metadatas = [doc.metadata.model_dump() for doc in documents]

        self.vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        return ids

    def search(
            self, query: str, top_k: int = 5, filters: Optional[Dict[str, str]] = None
    ):
        """Search for most relevant chunks based on query."""
        return self.vectorstore.similarity_search(query, k=top_k, filter=filters)

    def delete(self, ids: List[str]) -> None:
        """Delete chunks from ChromaDB by IDs."""
        self.vectorstore.delete(ids=ids)