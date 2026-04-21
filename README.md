# 📊 Multimodal 10-Q Financial Doc Q&A System

A production-grade full-stack AI system for **grounded question answering over SEC 10-Q filings**, designed with a focus on **reliability, validation, and controlled AI behavior**.

Unlike typical RAG demos, this system enforces **source grounding, scope validation, and fail-closed responses** to reduce hallucinations in financial analysis.

---

## 🚀 Overview

This system allows users to upload a company’s 10-Q filing and ask questions such as:

- What was revenue this quarter?
- What risks were mentioned?
- What was operating income?
- How did the company perform financially?

The system answers **only from the uploaded document** and provides **page-level citations**.

---

## 🧠 Key Features

### ✅ Grounded AI Answers
- Retrieval-based answers strictly from uploaded filings  
- Source citations (page-level)  
- No external or fabricated knowledge  

### 🧩 Agentic RAG Architecture
- Graph-based orchestration using LangGraph  
- Multi-step pipeline instead of single prompt  
- Includes:
  - retrieval
  - reranking
  - answer generation
  - hallucination detection
  - answer validation
  - retry / correction loops  

### 🛡️ Reliability & Safety Design
- Fail-closed behavior (refuses when evidence is insufficient)  
- Metadata-aware retrieval (ticker / period / scope)  
- Prevents wrong-company answers  
- Controlled LLM usage with deterministic components  

### 📄 Multimodal 10-Q Ingestion
- Parses text, tables, and charts from filings  
- Extracts metadata (ticker, year, quarter)  
- Converts charts/images into retrievable text summaries  

### ⚡ Performance Optimization
- Cross-encoder reranker for improved retrieval quality  
- Preloaded models to reduce first-query latency  
- Fast vs Full ingestion modes for cost/performance tradeoff  

---

## 🏗️ Architecture

The system is built as a **graph-based AI pipeline**:

User Query
↓
Query Routing
↓
Vector Retrieval (Qdrant)
↓
Reranking (Cross-Encoder)
↓
Answer Generation (LLM)
↓
Validation & Guardrails
↓
Final Answer (with citations OR refusal)


This design emphasizes **control over LLM behavior**, not just generation.

---

## 📥 Ingestion Pipeline

### Processing Steps:
- PDF upload → parsing → chunking  
- Metadata extraction (regex-first, LLM fallback)  
- Multimodal handling:
  - text
  - tables
  - charts/images → summarized into text  

### Stored Data Includes:
- ticker / year / quarter  
- page number  
- content type (text, table, image)  
- chunk relationships  

---

## 🔍 Retrieval System

- Vector DB: **Qdrant**
- Embeddings: sentence-transformers  
- Reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`  

Enhancements:
- Reranker preloaded at startup (reduces latency)
- Metadata filtering for scoped retrieval

---

## 🧪 Reliability Focus (Core Differentiator)

This project is designed around **AI system correctness**, not just functionality.

Key design decisions:
- Regex-first metadata extraction → reduces LLM errors  
- Source-aware generation → prevents hallucination  
- Explicit refusal when unsupported  
- Validation layers after generation  
- Scope-aware query handling (company / period)

---

## 🖥️ Tech Stack

### Backend
- Python, FastAPI  
- LangGraph, LangChain  
- OpenAI API  
- Qdrant  
- sentence-transformers + cross-encoder  
- unstructured (PDF parsing)  

### Frontend
- Next.js, React, TypeScript  
- Custom upload + chat UI  

### Infra / Deployment
- AWS ECS (Fargate), ECR  
- Application Load Balancer  
- CloudWatch, ACM  
- Cloudflare DNS  
- Vercel (frontend)  

---

## ⚙️ Deployment

- Backend: Dockerized → AWS ECS/Fargate  
- Frontend: Vercel  
- Secure HTTPS API via ALB + ACM  
- CI enabled (CD in progress)

---

## 🎯 What This Project Demonstrates

- Full-stack AI product development  
- Agentic RAG system design  
- Multimodal document processing  
- Vector search + reranking  
- LLM reliability engineering  
- Production deployment on AWS  

---

## 🚧 Current Status

The system is fully functional and deployed.

### Next Improvements
- Structured query analysis (intent + scope detection)  
- Stronger company/ticker validation  
- Better multi-company comparison handling  
- Enhanced rejection of unsupported financial queries  

---

## 📌 Positioning

This project is best understood as:

- **AI Engineer / GenAI Systems**
- **LLM + RAG + Agentic Pipeline**
- **Reliable AI System Design**

Not focused on:
- Pure model training
- Traditional ML pipelines
- Quantitative finance modeling

---

## 🔗 Demo & Repository

GitHub: https://github.com/shotitouch  
Live Demo: https://shotitouch-pdf-rag.vercel.app

---

## 👤 Author

Shotitouch Tuangcharoentip  
AI / Software Engineer | MS Machine Learning (Stevens Institute of Technology)
