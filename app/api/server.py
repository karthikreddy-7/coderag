# app/api/server.py
"""
FastAPI Server:
- Exposes REST API endpoints for UI/frontend
- Routes defined in `api/routes`
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import repos, chunks, queries
from app.db.init_db import *

app = FastAPI(
    title="CodeRAG API",
    description="API for indexing code repositories and answering questions about them.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok"}

app.include_router(repos.router)
app.include_router(chunks.router)
app.include_router(queries.router)
