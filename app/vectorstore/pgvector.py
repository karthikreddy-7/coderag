# app/vectorstore/pgvector.py
"""
Postgres + pgvector backend
"""

from .base import VectorStoreBase

class PGVectorStore(VectorStoreBase):
    def __init__(self, conn_str: str):
        pass
