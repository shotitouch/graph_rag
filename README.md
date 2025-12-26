# 🕸️ Agentic Graph PDF RAG — LangGraph + FastAPI + Next.js

A full-stack **Agentic Retrieval-Augmented Generation (RAG)** application implementing **self-correcting reasoning loops** for high-fidelity document intelligence.  
Built with **LangGraph**, **FastAPI**, **ChromaDB**, **BGE-Reranker**, and **Next.js**.

This project demonstrates advanced GenAI engineering including **agentic orchestration**, **multi-path intent routing**, and **two-stage retrieval** to mitigate hallucinations and improve answer reliability.

---

## 📌 Deployment Status

This project currently runs **locally only**.  
There is **no hosted instance yet**. Deployment plan:

- Frontend → **Vercel**
- Backend → **Render / Railway**
- Persistent Vector DB → Planned
- Public Demo → Planned

For now, users must:

1️⃣ Run FastAPI backend locally  
2️⃣ Run Next.js frontend locally  
3️⃣ Upload their own PDFs to chat with

---

## 🚀 Features

### 🤖 Agentic Intelligence
- LangGraph **stateful loop execution**
- Self-correction with iterative retrieval
- Failure & hallucination handling
- Intent routing for optimal reasoning paths

### 🔍 Smarter Retrieval
- **Two-Stage Retrieval**
  - ChromaDB dense retrieval
  - **BGE Cross-Encoder Reranker**
- Relevance confidence grading
- Context validation before generation

### ⚙️ Backend
- FastAPI with async streaming
- Structured JSON responses
- Citation-verified answers

### 🎨 Frontend
- Modern **Next.js** UI
- PDF upload support
- Interactive chat interface
- TailwindCSS styling

---

## 🧱 Tech Stack

### Backend
- FastAPI
- LangGraph + LangChain (LCEL)
- ChromaDB
- BGE-Reranker
- OpenRouter API
- Python 3.10+

### Frontend
- Next.js (TypeScript + React)
- TailwindCSS
- Axios

---

## 🏗 Architecture Overview

```
            ┌─────────────────────┐
            │     Next.js UI      │
            │ (Bento Grid + Chat) │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   FastAPI Backend   │
            │  (Async Streaming)  │
            └──────────┬──────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
  Ingest Pipeline              LangGraph Agent
  - PyPDFLoader                - Intent Router
  - Recursive Splitter         - Self-Correcting Loop
  - Embeddings Generation      - Hallucination Grader
        │                             │
        ▼                             ▼
  ┌──────────┐                ┌─────────────────┐
  │ ChromaDB │◄───────────────┤  BGE-Reranker   │
  └──────────┘                └─────────────────┘
```

---

## 📥 Backend Setup (FastAPI)

### 1️⃣ Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate       # Windows
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Environment variables

Create `.env` in backend root:

```
OPENROUTER_API_KEY=your_key_here
```

### 4️⃣ Run backend

```bash
uvicorn app.main:app --reload
```

Backend runs at:

👉 http://localhost:8000

---

## 💻 Frontend Setup (Next.js)

### 1️⃣ Install dependencies

```bash
npm install
```

### 2️⃣ Environment variables

Create `.env.local` in frontend root:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3️⃣ Run dev server

```bash
npm run dev
```

Frontend runs at:

👉 http://localhost:3000

---

## 🧠 How Agentic RAG Works

1️⃣ User query enters LangGraph **StateGraph**  
2️⃣ Initial retrieval from **ChromaDB**  
3️⃣ **BGE-Reranker** refines results  
4️⃣ Grader checks relevance quality  
5️⃣ If weak → rewrite query + re-retrieve  
6️⃣ LLM generates final answer with citations

---

## 👤 Author

**Shotitouch Tuangcharoentip**  
🎓 MS in Machine Learning, Stevens Institute of Technology (GPA 4.0)  
💻 5.5+ years Backend & Full‑Stack Engineering  
🚀 Focus: Agentic GenAI • Adversarial ML • Enterprise Systems

---

## 📜 License

MIT License
