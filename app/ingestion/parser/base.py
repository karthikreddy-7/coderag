from abc import ABC, abstractmethod
from typing import List

from app.db.schemas import ChunkDocument

"""
Base Parser Module

Defines the abstract base class `BaseParser` for all language-specific
parsers. Ensures consistent interface:
- parse_file(file_path): returns AST or structured representation
- extract_chunks(ast): returns list of logical chunks (methods/classes)
"""
class BaseParser(ABC):
    """Abstract base class for language-specific parsers."""

    @abstractmethod
    def parse_file(self, content: str):
        """
        Parse a source file content string and return AST representation.
        """
        pass

    @abstractmethod
    def extract_chunks(
        self,
        tree,
        content: str,
        repo_id: str,
        file_id: str,
        author: str = None,
        last_modified = None
    ) -> List[ChunkDocument]:
        """
        Extract logical code chunks from the AST.
        Returns a list of ChunkDocument objects.
        """
        pass