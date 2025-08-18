from __future__ import annotations
import logging
import json

from typing import Dict


from app.config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class utils:

    @staticmethod
    def _parse_json_object(raw: str) -> Dict:
        text = raw.strip()
        if text.startswith("```json"):
            text = text.replace("```json\n", "").replace("\n```", "")
        elif text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else ""
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
        try:
            return json.loads(text)
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {raw}. Error: {e}")
            return {"action": "error", "answer": "Failed to parse model output."}