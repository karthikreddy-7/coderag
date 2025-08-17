# app/ingestion/hashing.py
"""
Hashing:
- Compute and store hash for each file
- Detect changes efficiently
"""

import hashlib

class Hasher:
    def compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()
