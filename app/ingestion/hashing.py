# app/ingestion/hashing.py
"""
Hashing Module

Stateless utility to compute SHA-256 hashes and detect changes
for files based on provided current and previous hashes.
"""

import hashlib

class Hasher:
    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute SHA-256 hash of a string."""
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def has_changed(content: str, previous_hash: str = None) -> bool:
        """
        Determine if content has changed compared to previous hash.

        Args:
            content (str): Current file content.
            previous_hash (str, optional): Previously stored hash. Defaults to None.

        Returns:
            bool: True if changed or new, False otherwise.
        """
        current_hash = Hasher.compute_hash(content)
        if previous_hash != current_hash:
            return True
        return False
