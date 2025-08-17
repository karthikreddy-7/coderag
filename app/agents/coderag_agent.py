# app/agents/coderag_agent.py
"""
CodeRAG Agent:
- Handles technical queries on codebase
- Uses tools like context retrieval, file fetch, etc.
- Returns final structured answer to MasterAgent
"""

from langchain.prompts import PromptTemplate

from .LLM_Manager import LLM
from .prompts import CODERAG_PROMPT_TEMPLATE
from .tools import AgentTools


class CodeRAGAgent:
    def __init__(self, tools: AgentTools):
        self.tools = tools
        self.llm = LLM(temperature=0)
        self.prompt_template = PromptTemplate.from_template(CODERAG_PROMPT_TEMPLATE)

    def answer_query(self, query: str, repo_id: str) -> str:
        """Answer a query using the retrieve-and-generate pattern."""
        # 1. Retrieve context
        context = self.tools.get_more_context(query, repo_id)
        if not context or "Error:" in context:
            return "Could not retrieve relevant context to answer the question."

        # 2. Build the prompt
        prompt = self.prompt_template.format(context=context, query=query)

        # 3. Generate the answer
        response = self.llm.invoke(prompt)
        return response.content
