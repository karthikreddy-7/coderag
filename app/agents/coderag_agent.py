from __future__ import annotations
import logging
import json

from typing import Dict

from app.agents.LLM_Manager import LLM
from app.agents.prompts import DECISION_PROMPT
from app.agents.tools import AgentTools
from app.config.logging_config import setup_logging
from app.db.schemas import AgentResponse
from app.utils import utils

setup_logging()
logger = logging.getLogger(__name__)


class CoderagAgent:
    """
    A simplified agent that:
    1. Starts by retrieving initial context for the query.
    2. Initializes the loop with this enriched context.
    3. In each loop:
        - Ask the LLM to decide which tool to use (or answer directly).
        - Execute tool if chosen.
        - Feed results back as the new context.
    4. Logs each raw LLM response for debugging.
    5. If the loop ends without a direct answer, forces a final summarization step.
    """
    def __init__(self, tools: AgentTools):
        self.tools = tools.get_tools()
        self.llm = LLM()
        self.max_loops = 3

    def handle_query(self, query: str, repo_id: int) -> Dict:
        tool_calls = []
        # Step 0: Retrieve initial context
        logger.info("Retrieving initial context before starting loop...")
        initial_context = self.tools["get_more_context"](
            query=query, repo_id=str(repo_id), top_k=3
        )
        current_thought = (
            f"The user asked: {query}\n\n"
            f"Here is the initial retrieved context:\n{initial_context}"
        )
        final_answer = None
        action = None  # track last LLM decision
        for i in range(self.max_loops):
            logger.info(f"Agent loop {i + 1}/{self.max_loops}. Current thought prepared.")
            # Step 1: Construct prompt for LLM
            decision_prompt = DECISION_PROMPT.format(
                question=current_thought,
                repo_id=str(repo_id),
                tools_desc=(
                    "get_more_context(query: str, repo_id: str) -> str: "
                    "Finds relevant code snippets based on a query.\n"
                    "get_specific_file(file_path: str, repo_id: str) -> str: "
                    "Fetches the entire content of a specific file."
                )
            )
            # Step 2: Call LLM and log raw output
            decision_raw = self._safe_invoke(decision_prompt)
            logger.info(f"Raw LLM Response (loop {i+1}): {decision_raw}")
            # Step 3: Parse response
            decision = utils._parse_json_object(decision_raw)
            action = decision.get("action", "answer")
            tool_input = decision.get("tool_input", {})

            # Step 4: Execute chosen action
            if action in self.tools:
                logger.info(f"LLM chose tool: {action} with input: {tool_input}")
                tool_function = self.tools[action]

                if "repo_id" not in tool_input:
                    tool_input["repo_id"] = str(repo_id)

                try:
                    tool_output = tool_function(**tool_input)
                    tool_calls.append({
                        "tool": action,
                        "input": tool_input,
                        "output": tool_output[:1000]  # truncate
                    })
                    current_thought = (
                        f"The user asked: {query}\n"
                        f"So far, I retrieved this information:\n{tool_output}\n\n"
                        "Now decide whether you can directly answer the user or if you need another tool."
                    )
                except Exception as e:
                    logger.error(f"Error executing tool '{action}': {e}")
                    tool_calls.append({
                        "tool": action,
                        "input": tool_input,
                        "error": str(e)
                    })
                    current_thought = (
                        f"The tool '{action}' failed. Error: {e}. "
                        f"Try a different approach to answer the user's question."
                    )
            else:
                logger.info("LLM chose to answer directly or gave invalid action. Ending loop.")
                final_answer = (
                        decision.get("answer")
                        or decision.get("tool_input", {}).get("answer")
                        or "No direct answer provided."
                )
                break
        # -----------------------
        # Final summarizer fallback
        # -----------------------
        if action != "answer":
            logger.info("Loop ended without natural answer. Forcing final summarization.")
            summary_prompt = f"""
            The user asked: {query}

            Here are the tool results collected:
            {json.dumps(tool_calls, indent=2)}

            Please summarize this into a clear natural-language answer for the user.
            """
            final_answer = self._safe_invoke(summary_prompt)
        return AgentResponse(
            status="final",
            answer=final_answer,
            tool_calls=tool_calls,
        ).to_dict()

    def _safe_invoke(self, prompt: str) -> str:
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            logger.exception("LLM invocation failed")
            return f'{{"action": "error", "answer": "LLM invocation failed: {e}"}}'

