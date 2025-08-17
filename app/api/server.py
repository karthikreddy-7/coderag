# app/api/server.py
"""
FastAPI Server:
- Exposes REST API endpoints for UI/frontend
- Routes defined in `api/routes`
"""

from fastapi import FastAPI

app = FastAPI(title="CodeRAG API")

# Import routes
from .routes import repos, chunks, queries
app.include_router(repos.router)
app.include_router(chunks.router)
app.include_router(queries.router)
