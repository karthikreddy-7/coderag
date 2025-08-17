from abc import ABC, abstractmethod

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
    def parse_file(self, file_path: str):
        """Parse a source file and return AST representation."""
        pass

    @abstractmethod
    def extract_chunks(self, ast):
        """Extract logical code chunks from AST (methods, classes)."""
        pass
