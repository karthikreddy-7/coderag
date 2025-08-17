#!/bin/bash
# Run FastAPI server
uvicorn app.api.server:app --reload --port 8000
