# app/agents/master_agent.py
"""
Master Agent:
- Entry point for user queries
- Handles ambiguity resolution (ask user if unclear)
- Routes refined queries to the CodeRAG agent
- Maintains context of Q/A history
"""

class MasterAgent:
    def __init__(self):
        # Initialize state tracking
        self.conversation_history = []

    def handle_query(self, query: str):
        """Process a query, refine it, and delegate to CodeRAGAgent."""
        pass

    def refine_query(self, query: str) -> str:
        """Return a clarified/brief version of query or ask user for clarification."""
        pass
