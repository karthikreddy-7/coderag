from datetime import datetime
from typing import List, Union
from uuid import uuid4
from app.ingestion.parser.base import BaseParser
from app.db.schemas import ChunkDocument, ChunkMetadata
import javalang
from javalang.tree import Node

"""
Java Parser Module
Implements the `BaseParser` interface for Java source files.
Responsible for parsing Java files into ASTs and extracting
logical chunks such as methods and classes. Can be extended
with additional Java parsing tools like javalang or tree-sitter.
"""


class JavaParser(BaseParser):
    def parse_file(self, content: str):
        """
        Parse Java file content and return an AST-like tree.
        """
        tree = javalang.parse.parse(content)
        return tree

    def _get_node_end_line(self, node: Node) -> int:
        """
        Recursively find the maximum line number in a node's subtree.
        This provides a much better, though not always perfect, approximation
        for the end line, as javalang doesn't store end positions.
        """
        max_line = node.position.line if node.position else 0

        for child in node:
            if isinstance(child, Node):
                max_line = max(max_line, self._get_node_end_line(child))
            elif isinstance(child, list):
                for item in child:
                    if isinstance(item, Node):
                        max_line = max(max_line, self._get_node_end_line(item))
        return max_line

    def extract_chunks(self, tree, content: str, repo_id: str, file_id: str, author=None, last_modified=None) -> List[
        ChunkDocument]:
        chunks = []
        lines = content.splitlines()
        for path, node in tree:
            # We are interested in classes and methods
            if isinstance(node, (javalang.tree.ClassDeclaration, javalang.tree.MethodDeclaration)):
                start_line = node.position.line if node.position else 1
                # Use the recursive helper to find a more accurate end line
                end_line = self._get_node_end_line(node)
                # Ensure end_line does not exceed the total number of lines
                if end_line > len(lines):
                    end_line = len(lines)
                # Find the actual end line by looking for the closing brace '}'
                # This makes the end_line capture complete blocks
                brace_found = False
                for i in range(end_line - 1, len(lines)):
                    if '}' in lines[i]:
                        end_line = i + 1
                        brace_found = True
                        break
                if not brace_found:
                    end_line = len(lines)
                # Avoid creating empty or out-of-bounds snippets
                if start_line > end_line:
                    continue
                snippet = lines[start_line - 1:end_line]
                chunk = ChunkDocument(
                    content="\n".join(snippet),
                    metadata=ChunkMetadata(
                        chunk_id=str(uuid4()),
                        file_id=file_id,
                        repo_id=repo_id,
                        start_line=start_line,
                        end_line=end_line,
                        language="java",
                        author=author,
                        last_modified=last_modified or datetime.utcnow()
                    )
                )
                chunks.append(chunk)
        return chunks


if __name__ == "__main__":
    sample_java = """
    package com.example;
    public class HelloWorld {
        public void sayHello() {
            System.out.println("Hello, world!");
        }
        public int add(int a, int b) {
            return a + b;
        }
    }
    """
    parser = JavaParser()
    tree = parser.parse_file(sample_java)
    chunks = parser.extract_chunks(tree, sample_java, repo_id="test_repo", file_id="hello.java")
    print(f"Extracted {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"Chunk ID: {chunk.metadata.chunk_id}")
        print(f"Lines {chunk.metadata.start_line}-{chunk.metadata.end_line}")
        print(chunk.content)
        print("-" * 40)