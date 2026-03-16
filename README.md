# Agentic Graph PDF RAG

A full-stack agentic Retrieval-Augmented Generation system for grounded question answering over uploaded PDF documents. The application uses LangGraph orchestration, Chroma retrieval, reranking, iterative query rewriting, and source-aware answer generation.

## Architecture

```text
Next.js frontend
  -> FastAPI API
  -> LangGraph workflow
  -> retrieval + reranking
  -> answer generation + citations
```

## Tech Stack

### Backend
- Python 3.11
- FastAPI
- LangGraph
- LangChain
- ChromaDB
- OpenAI-compatible chat and embedding models
- sentence-transformers reranker

### Frontend
- Next.js
- TypeScript
- React

## Environment Variables

### Backend

Copy `server/.env.example` to `server/.env` and set:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
PERSIST_DIR=./chroma_db
```

### Frontend

Copy `frontend/.env.local.example` to `frontend/.env.local` and set:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Local Run Without Docker

### Backend

```bash
cd server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Run With Docker Compose

1. Create `server/.env` from `server/.env.example`
2. Run:

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

## Notes

- The backend stores Chroma data in a named Docker volume when run through Compose.
- The frontend container uses `NEXT_PUBLIC_API_URL=http://localhost:8000` inside the Docker network.
- This repository is being productionized incrementally, with observability and deployment maturity added in phases.
