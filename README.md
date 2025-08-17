# CodeRAG

🚀 **CodeRAG** is a code-aware **Retrieval-Augmented Generation (RAG)** system designed for software repositories.  
It ingests code, chunks it efficiently, embeds it, stores it in a vector database, and exposes APIs + UI for semantic search and intelligent code queries.

---

## ✨ Features
- 📂 Code ingestion pipeline: chunking, parsing, hashing, embedding, indexing
- 🤖 Agents for orchestrating queries, tools, and responses
- 🔎 Multi-vectorstore support: Chroma, PGVector, Weaviate
- ⚡ FastAPI backend with modular APIs (chunks, queries, repos)
- 🖥️ React + TypeScript frontend with a chat-style UI
- 🛠️ Scripts for database initialization and repository re-indexing
- 🔧 Config-driven (settings + logging)

---

## 📂 Project Structure

```
coderag/
├── app/                # Python backend
│   ├── agents/         # CoderAG agents (orchestration, tools)
│   ├── api/            # FastAPI routes and server
│   ├── config/         # Logging and settings
│   ├── db/             # CRUD, models, schemas, session
│   ├── ingestion/      # Chunking, embedding, parsing, indexing
│   ├── vectorstore/    # Vectorstore integrations
│   └── temp.py         # Scratch/experiments
│
├── scripts/            # Utility scripts
│   ├── init_db.py      # Initialize DB schema
│   ├── reindex_repo.py # Re-index repositories
│   └── run_server.sh   # Run backend server
│
├── ui/                 # React + TypeScript frontend
│   ├── src/            # Main source code
│   │   ├── components/ # Chat, CodeViewer, Layout, Repository, UI kit
│   │   ├── hooks/      # Custom hooks
│   │   ├── lib/        # API client, store, utils
│   │   ├── pages/      # Routes (Index, NotFound)
│   │   └── types/      # Type definitions
│   └── public/         # Static assets
│
├── requirements.txt    # Python dependencies
├── README.md           # Project docs
└── ...
```

## ⚙️ Backend Setup (Python)
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize DB
python scripts/init_db.py

# Run server
bash scripts/run_server.sh
```
Backend will start on http://localhost:8000.

## 🎨 Frontend Setup (React + TypeScript)
```bash
cd ui
npm install    # or bun install / yarn
npm run dev
```
Frontend runs at http://localhost:5173.

## 🧩 Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic 
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2, etc.)
- Vectorstores: Chroma, PGVector, Weaviate
- Frontend: React, TypeScript, Vite, TailwindCSS, shadcn/ui
- DB: SQLite (default) / Postgres (production)


## 🤝 Contributing

Contributions are welcome! Open a PR or start a discussion if you’d like to add new features or improvements.