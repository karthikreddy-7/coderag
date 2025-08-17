# app/vectorstore/base.py
"""
VectorStore Base:
- Defines standard interface for all backends
"""

class VectorStoreBase:
    def add_embeddings(self, embeddings):
        pass

    def query(self, query_embedding, top_k: int):
        pass
