# app/config/settings.py
"""
App Settings:
- Static/dynamic configuration values
- Example: DB URI, vectorstore backend
"""
import os

# Base directory (where models are stored)
BASE_DIR = "/home/karthik/dev/coderag/"

# --- Vector Store Configuration ---
# Define the directory for ChromaDB persistence
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")


# Local embedding model path
EMBEDDING_MODEL_PATH = os.path.join("/home/karthik/dev/", "models", "all-MiniLM-L6-v2")

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'coderag.db')}"
VECTOR_BACKEND = "chroma"

GITLAB_API_BASE = "https://gitlab.com/api/v4"
PRIVATE_TOKEN = ""
GOOGLE_API_KEY=""

# Whitelist: Only include files with these extensions
ALLOWED_EXTENSIONS = {".java", ".xml", ".properties",".yml"}

# Blacklist: Exclude any files or folders with these exact names
IGNORED_FOLDERS = {"target", "build", "node_modules", ".git", ".idea", ".vscode","test",".mvn"}
IGNORED_FILES = {"pom.xml", "mvnw", "mvnw.cmd"}
