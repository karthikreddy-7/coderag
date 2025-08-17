# app/ingestion/chunker.py
"""
Chunker Module

Responsible for breaking source code files into logical chunks,
such as methods, classes, or functions. Works with the output
of language-specific parsers to produce structured chunks
ready for embedding and storage in the vector store.
"""


class Chunker:
    def chunk_file(self, ast):
        """Return list of chunks from AST."""
        pass
