# app/config/settings.py
"""
App Settings:
- Static/dynamic configuration values
- Example: DB URI, vectorstore backend
"""
import os

# Base directory (where models are stored)
BASE_DIR = "/home/karthik/dev/"

# Local embedding model path
EMBEDDING_MODEL_PATH = os.path.join(BASE_DIR, "models", "all-MiniLM-L6-v2")

DATABASE_URL = "sqlite:///./coderag.db"
VECTOR_BACKEND = "chroma"

GITLAB_API_BASE = "https://gitlab.com/api/v4"

