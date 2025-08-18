# app/db/schemas.py
"""
Pydantic Schemas:
- Define request/response models for API
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional, List, Any


class ChunkMetadata(BaseModel):
    """
    Metadata schema for a single chunk of code/text.
    This acts as a DTO (Data Transfer Object) across the project.
    """
    chunk_id: str
    file_id: str
    repo_id: str
    class_context: Optional[str]
    start_line: int
    end_line: int
    language: Optional[str] = None
    author: Optional[str] = None
    last_modified: Optional[str] = None

class ChunkDocument(BaseModel):
    """
    Document schema that wraps content with its metadata.
    """
    content: str
    metadata: ChunkMetadata

# ---------- Response model ----------
@dataclass
class AgentResponse:
    status: str
    answer: str
    tool_calls: List[Dict[str, Any]]

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "answer": self.answer,
            "meta": {
                "tool_calls": self.tool_calls,
            },
        }



