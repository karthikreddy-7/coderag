# app/agents/coderag_agent.py
from __future__ import annotations
import logging
import json
from dataclasses import dataclass
from typing import Dict, Optional

from app.agents.LLM_Manager import LLM
from app.agents.prompts import DECISION_PROMPT, SYNTHESIS_PROMPT
from app.agents.tools import AgentTools

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ---------- Response model ----------
@dataclass
class AgentResponse:
    status: str
    answer: str
    action_taken: str
    tool_input: str
    used_context_preview: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "answer": self.answer,
            "meta": {
                "action_taken": self.action_taken,
                "tool_input": self.tool_input,
                "used_context_preview": (
                    (self.used_context_preview[:800] + "…")
                    if self.used_context_preview and len(self.used_context_preview) > 800
                    else self.used_context_preview
                ),
            },
        }


class CoderagAgent:
    """
    Simple Agentic-RAG:
      1. Embed query + retrieve relevant context
      2. Tell LLM about available tools
      3. LLM decides: answer directly, or call a tool
      4. If tool is called → use it, then synthesize final answer
    """

    def __init__(self, tools: AgentTools):
        self.tools = tools.get_tools()
        self.get_more_context = self.tools["get_more_context"]
        self.get_specific_file = self.tools["get_specific_file"]
        self.llm = LLM()

    def handle_query(self, query: str, repo_id: int) -> Dict:
        logger.info("Retrieving embeddings for query…")
        initial_context = self.get_more_context(query=query, repo_id=str(repo_id))

        # Step 1: Ask LLM what to do (with context + tool descriptions)
        decision_prompt = DECISION_PROMPT.format(
            query=query,
            repo_id=str(repo_id),
            context_preview=initial_context[:1500],  # small chunk
            tools_desc="You can call: get_more_context(query), get_specific_file(file_path)."
        )
        decision_raw = self._safe_invoke(decision_prompt)
        decision = self._parse_json_object(decision_raw)

        action = decision.get("action", "answer")
        tool_input = decision.get("tool_input", "").strip()

        if action == "get_more_context":
            logger.info("LLM chose tool: get_more_context")
            context = self.get_more_context(query=tool_input or query, repo_id=str(repo_id))
        elif action == "get_specific_file":
            logger.info("LLM chose tool: get_specific_file")
            context = self.get_specific_file(file_path=tool_input, repo_id=str(repo_id))
        else:
            logger.info("LLM chose to answer directly")
            context = initial_context

        # Step 2: Final synthesis
        synthesis_prompt = SYNTHESIS_PROMPT.format(question=query, context=context[:6000])
        final_answer = self._safe_invoke(synthesis_prompt)

        return AgentResponse(
            status="final",
            answer=final_answer,
            action_taken=action,
            tool_input=tool_input,
            used_context_preview=context,
        ).to_dict()

    # ---------- Utilities ----------
    def _safe_invoke(self, prompt: str) -> str:
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            logger.exception("LLM invocation failed")
            return f"Error: {e}"

    @staticmethod
    def _parse_json_object(raw: str) -> Dict:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else ""
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
        try:
            return json.loads(text)
        except Exception:
            return {}
