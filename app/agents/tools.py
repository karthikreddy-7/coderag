# app/agents/tools.py
"""
Agent Tools:
- Provides helper methods like:
    - get_more_context(query)
    - get_specific_file(path)
- Tools are invoked by CodeRAGAgent
"""

class AgentTools:
    def get_more_context(self, query: str):
        """Retrieve broader context for a query (via vector store)."""
        pass

    def get_specific_file(self, file_path: str):
        """Fetch raw code file content by path."""
        pass
