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
PRIVATE_TOKEN = ""


# Whitelist: Only include files with these extensions
ALLOWED_EXTENSIONS = {".java", ".xml", ".properties",".yml"}

# Blacklist: Exclude any files or folders with these exact names
IGNORED_FOLDERS = {"target", "build", "node_modules", ".git", ".idea", ".vscode","test"}
IGNORED_FILES = {"pom.xml", "mvnw", "mvnw.cmd"}
