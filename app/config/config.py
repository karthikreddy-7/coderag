import os

# Base directory (where models are stored)
BASE_DIR = "/home/karthik/dev/"

# Local embedding model path
EMBEDDING_MODEL_PATH = os.path.join(BASE_DIR, "models", "all-MiniLM-L6-v2")

# app/config/config.py
"""
Configuration Loader:
- Reads from settings.py or environment
- Provides centralized config access
"""

class Config:
    def __init__(self):
        # Load values from env or settings
        pass
