# app/agents/coderag_agent.py
"""
CodeRAG Agent:
- Handles technical queries on codebase
- Uses tools like context retrieval, file fetch, etc.
- Returns final structured answer to MasterAgent
"""

class CodeRAGAgent:
    def __init__(self, tools):
        self.tools = tools

    def answer_query(self, query: str):
        """Answer query using embeddings + tools (chunk retrieval, file fetch)."""
        pass
