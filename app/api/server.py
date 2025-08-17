# app/api/server.py
"""
FastAPI Server:
- Exposes REST API endpoints for UI/frontend
- Routes defined in `api/routes`
"""
from fastapi import FastAPI
from app.api.routes import repos, chunks, queries


app = FastAPI(
    title="CodeRAG API",
    description="API for indexing code repositories and answering questions about them.",
    version="1.0.0"
)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok"}

app.include_router(repos.router)
app.include_router(chunks.router)
app.include_router(queries.router)
