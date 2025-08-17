from datetime import datetime, timezone
from typing import List, Optional
from app.ingestion.parser.base import BaseParser
from app.db.schemas import ChunkDocument, ChunkMetadata
import os
import hashlib

from tree_sitter import Language, Parser, Node


class JavaParser(BaseParser):
    """
    A robust Java parser that uses semantic signatures for deterministic chunk IDs.
    """
    CHUNKABLE_NODE_TYPES = {
        'method_declaration',
        'constructor_declaration',
        'interface_declaration',
        'enum_declaration',
    }

    def __init__(self):
        """Initializes the tree-sitter parser with the Java grammar."""
        lib_path = os.path.join(os.path.dirname(__file__), '..', '..', 'build', 'my-languages.so')
        self.JAVA_LANGUAGE = Language(lib_path, 'java')
        self.parser = Parser()
        self.parser.set_language(self.JAVA_LANGUAGE)

    def parse_file(self, content: str) -> Node:
        """Parse Java file content and return a tree-sitter AST."""
        tree = self.parser.parse(bytes(content, "utf8"))
        return tree.root_node

    def _find_parent_class_context(self, node: Node) -> Optional[str]:
        """Traverses up the tree from a node to find the name of its containing class."""
        current = node.parent
        while current:
            if current.type == 'class_declaration':
                name_node = current.child_by_field_name('name')
                if name_node:
                    return name_node.text.decode('utf8')
            current = current.parent
        return None

    def _get_node_signature(self, node: Node, class_name: str) -> str:
        """Extracts a unique signature from a method or constructor node."""
        signature_parts = [class_name]
        if node.type == 'constructor_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                signature_parts.append(name_node.text.decode('utf8'))
        elif node.type == 'method_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                signature_parts.append(name_node.text.decode('utf8'))
        params_node = node.child_by_field_name('parameters')
        if params_node:
            signature_parts.append(params_node.text.decode('utf8'))
        return ":".join(signature_parts)

    def _traverse_and_chunk(
            self,
            node: Node,
            imports_block: str,
            repo_id: str,
            file_id: str,
            author: Optional[str],
            last_modified: Optional[datetime]
    ) -> List[ChunkDocument]:
        """Recursively traverses the AST, creating a flat list of context-rich chunks."""
        chunks = []
        if node.type in self.CHUNKABLE_NODE_TYPES:
            class_context = self._find_parent_class_context(node)
            if not class_context:
                return []
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            content_text = node.text.decode('utf8')
            comment_text = ""
            if node.prev_named_sibling and node.prev_named_sibling.type == 'block_comment':
                comment_node = node.prev_named_sibling
                comment_text = comment_node.text.decode('utf8') + '\n'
                start_line = comment_node.start_point[0] + 1
            full_content = f"{imports_block}\n\n{comment_text}{content_text}"
            signature = self._get_node_signature(node, class_context)
            id_string = f"{repo_id}:{file_id}:{signature}"
            chunk_id = hashlib.sha256(id_string.encode('utf-8')).hexdigest()

            chunk = ChunkDocument(
                content=full_content.strip(),
                metadata=ChunkMetadata(
                    chunk_id=chunk_id,  # Use the new signature-based ID
                    file_id=file_id,
                    repo_id=repo_id,
                    start_line=start_line,
                    end_line=end_line,
                    language="java",
                    author=author,
                    last_modified=datetime.now(timezone.utc).isoformat(),
                    class_context=class_context
                )
            )
            chunks.append(chunk)

        for child in node.children:
            chunks.extend(self._traverse_and_chunk(child, imports_block, str(repo_id), file_id, author, last_modified))

        return chunks

    def extract_chunks(
            self,
            root_node: Node,
            content: str,
            repo_id: str,
            file_id: str,
            author=None,
            last_modified=None
    ) -> List[ChunkDocument]:
        """Extracts a flat list of context-rich chunks from a file's AST root node."""
        import_nodes = [node for node in root_node.children if node.type == 'import_declaration']
        imports_block = "\n".join(node.text.decode('utf8') for node in import_nodes)
        return self._traverse_and_chunk(root_node, imports_block, repo_id, file_id, author, last_modified)


if __name__ == "__main__":
    sample_java = """package com.example.webrest;

import org.springframework.web.bind.annotation.*;
import com.example.model.Order;

/**
 * REST Controller for managing customer orders.
 */
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    public OrderController() {
        // Constructor
    }

    /**
     * Retrieves an order by its unique ID.
     * @param id The ID of the order.
     * @return A ResponseEntity containing the Order if found.
     */
    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrderById(@PathVariable String id) {
        return orderService.findById(id)
                .map(ResponseEntity::ok)
                .orElseThrow(() -> new OrderNotFoundException(id));
    }
}
"""
    parser = JavaParser()
    tree = parser.parse_file(sample_java)
    chunks = parser.extract_chunks(tree, sample_java, repo_id="test_repo", file_id="OrderController.java")

    print(f"Extracted {len(chunks)} chunks:")
    for chunk in chunks:
        print("-" * 50)
        print(f"Chunk ID: {chunk.metadata.chunk_id}")
        # Assuming your ChunkMetadata schema is updated, this will work
        print(f"Class Context: {chunk.metadata.class_context}")
        print(f"Lines: {chunk.metadata.start_line}-{chunk.metadata.end_line}")
        print(chunk.content)
