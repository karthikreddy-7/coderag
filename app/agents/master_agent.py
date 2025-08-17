# app/agents/master_agent.py
"""
Master Agent:
- Entry point for user queries
- Handles ambiguity resolution (ask user if unclear)
- Routes refined queries to the CodeRAG agent
- Maintains context of Q/A history
"""

from langchain.prompts import PromptTemplate

from .LLM_Manager import LLM
from .prompts import MASTER_PROMPT_TEMPLATE
from .coderag_agent import CodeRAGAgent
from .tools import AgentTools


class MasterAgent:
    def __init__(self, tools: AgentTools):
        self.tools = tools
        self.coderag_agent = CodeRAGAgent(tools)
        self.conversation_history = []
        self.llm = LLM(temperature=0)
        self.refine_prompt_template = PromptTemplate.from_template(MASTER_PROMPT_TEMPLATE)

    def refine_query(self, query: str) -> str:
        """Refines a query using conversation history."""
        history_str = "\n".join([f"Q: {q}\nA: {a}" for q, a in self.conversation_history])
        prompt = self.refine_prompt_template.format(history=history_str, query=query)
        response = self.llm.invoke(prompt)
        return response.content

    def handle_query(self, query: str, repo_id: int) -> str:
        """Process a query, refine it, and delegate to CodeRAGAgent."""
        self.conversation_history.append(("User", query))

        # 1. Refine the query
        refined_query = self.refine_query(query)
        print(f"Original Query: '{query}'\nRefined Query: '{refined_query}'")

        # 2. Delegate to CodeRAG agent
        answer = self.coderag_agent.answer_query(refined_query, repo_id)

        # 3. Update history
        self.conversation_history.append(("AI", answer))

        return answer
