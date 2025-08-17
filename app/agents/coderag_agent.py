# app/agents/coderag_agent.py
from app.agents.LLM_Manager import LLM
from app.agents.tools import AgentTools
import json
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CoderagAgent:
    """
    Master agent that decides which tool to use, executes it, and then synthesizes
    a final answer using the tool's output.
    Returns a strictly JSON output representing the final answer or the next action.
    """

    DECISION_PROMPT_TEMPLATE = """
You are an expert software engineering assistant. Your primary goal is to answer questions about a code repository.
Based on the user's question, you must decide on one of three actions.

Here are your available tools:

1.  `get_more_context(query: str, repo_id: str)`: Use this for broad, conceptual questions or when comparing multiple files/concepts. For example: "How does the authentication system work?" or "What's the difference between ServiceA and ServiceB?".
2.  `get_specific_file(file_path: str, repo_id: str)`: Use this when the user explicitly asks for the contents of a specific file path. For example: "Can you show me the code in 'src/utils/helpers.py'?".
3.  `ask_user`: Use this only when the user's question is too ambiguous or lacks the necessary information to use a tool effectively. For example: "What does it do?".

First, think step-by-step about what the user is asking and which tool is most appropriate. Then, provide your final decision as a single, valid JSON object.

**Do NOT answer the question directly.** Your only job is to choose the action.

**Output Format:**
{{
    "action": "<one of: get_more_context, get_specific_file, ask_user>",
    "tool_input": "<string input for the tool, or a clarifying question for the user>",
    "response": ""
}}

Ensure your output is ONLY the JSON object, with no other text or code fences.

User Question: "{query}"
Repo ID: {repo_id}
"""

    SYNTHESIS_PROMPT_TEMPLATE = """
You are an expert software engineering assistant. You have been provided with a user's question and some context retrieved from a code repository. Your task is to use this context to formulate a clear, concise, and accurate answer to the user's question.

If the context is insufficient or does not seem relevant, state that you couldn't find the specific information. Do not invent details.

Original User Question: "{query}"

Retrieved Context:
---
{context}
---

Your Answer:
"""

    def __init__(self, tools: AgentTools):
        self.tools = tools.get_tools()
        self.get_more_context = self.tools[0]
        self.get_specific_file = self.tools[1]
        self.llm = LLM()

    def handle_query(self, query: str, repo_id: int) -> dict:
        """
        Processes a query in a multi-step loop:
        1.  LLM decides which action to take (Reason).
        2.  The chosen tool is executed (Act).
        3.  LLM uses the tool's output to synthesize a final answer.
        """
        # --- Step 1: Decide which action to take ---
        logging.info(f"Step 1: Deciding action for query: '{query}'")
        decision_prompt = self.DECISION_PROMPT_TEMPLATE.format(query=query, repo_id=repo_id)
        raw_response = self.llm.invoke(decision_prompt)
        cleaned_response = self.clean_code_fence(raw_response)

        try:
            decision = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse decision JSON: {e}\nRaw response: {raw_response}")
            return {"action": "ask_user", "tool_input": "I had an internal error processing your request. Could you please rephrase it?", "response": ""}

        action = decision.get("action")
        tool_input = decision.get("tool_input")
        repo_id_str = str(repo_id)  # For Pydantic validation in tools
        print(cleaned_response)

        # --- Step 2: Execute the action ---
        logging.info(f"Step 2: Executing action '{action}' with input '{tool_input}'")
        context = ""
        if action == "get_more_context" and tool_input:
            context = self.get_more_context.invoke({
                "query": tool_input,
                "repo_id": repo_id_str
            })
        elif action == "get_specific_file" and tool_input:
            context = self.get_specific_file.invoke({
                "file_path": tool_input,
                "repo_id": repo_id_str
            })
        elif action == "ask_user":
            # If the decision is to ask the user, we stop here.
            return {
                "action": "ask_user",
                "tool_input": tool_input,
                "response": "I need more information to proceed. " + tool_input
            }
        else:
             # Fallback if the action is invalid or missing input
            logging.warning(f"Invalid action '{action}' or missing tool_input. Asking user for clarification.")
            return {
                "action": "ask_user",
                "tool_input": query,
                "response": "I was unable to determine the right tool for your query. Could you be more specific?"
            }

        # --- Step 3: Synthesize the final answer ---
        logging.info("Step 3: Synthesizing final answer from context.")
        synthesis_prompt = self.SYNTHESIS_PROMPT_TEMPLATE.format(query=query, context=context)
        print(synthesis_prompt)
        final_answer = self.llm.invoke(synthesis_prompt)

        return {
            "action": "final_answer",
            "tool_input": tool_input, # Provides context on what tool was used
            "response": final_answer
        }

    @staticmethod
    def clean_code_fence(raw: str) -> str:
        """Remove ```json or ``` fences and extra whitespace."""
        if raw.startswith("```"):
            # Handles both ```json and ```
            raw = raw.split("\n", 1)[1] if "\n" in raw else ""
        if raw.endswith("```"):
            raw = raw.rsplit("\n", 1)[0] if "\n" in raw else ""
        return raw.strip()

# -----------------------------
# Smoke test
# -----------------------------
if __name__ == "__main__":
    from app.db.session import get_db_session
    from app.vectorstore.chroma import ChromaVectorStore
    from app.agents.tools import AgentTools

    db = get_db_session()
    vectorstore = ChromaVectorStore()
    tools = AgentTools(db=db, vectorstore=vectorstore)
    agent = CoderagAgent(tools=tools)

    test_queries = [
        {"repo_id": 1, "query": "Can you tell me how UserResumeController is different from UserGenerationController ?"},
    ]

    for i, q in enumerate(test_queries, 1):
        result = agent.handle_query(query=q["query"], repo_id=q["repo_id"])
        print(result)