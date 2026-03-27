## Agentic Graph PDF RAG

A full-stack **agentic Retrieval-Augmented Generation (RAG)** system for grounded question answering over uploaded PDF documents. Built with **LangGraph**, **FastAPI**, **Next.js**, **Qdrant**, and a reranking layer, the system combines retrieval, query rewriting, citation-aware generation, and validation loops to improve answer quality and reduce unsupported responses.

This project demonstrates practical **AI systems engineering** through **agentic orchestration**, **multi-stage retrieval**, **structured observability**, **CI**, and a **deployment-oriented architecture**. It is designed as a production-minded LLM application rather than a simple chatbot demo, with emphasis on grounded answers, traceable behavior, and reliability-aware control flow.

### Features

#### Agentic Intelligence
- LangGraph-based stateful workflow orchestration
- Query rewriting and retry loops for weak retrieval cases
- Hallucination and answer-quality grading
- Intent-based routing between conversational and document-grounded paths

#### Retrieval and Grounding
- Dense retrieval over **Qdrant**
- Cross-encoder reranking for improved context precision
- Citation-aware answer generation
- Fail-closed response behavior for unsupported answers

#### Backend
- FastAPI service for ingestion and question answering
- Structured JSON responses with sources
- Structured logging, request tracing, and per-node latency instrumentation
- Dockerized backend with CI-based validation

#### Frontend
- Next.js interface for PDF upload and chat
- Source-aware responses with citations
- TypeScript-based client application

### Tech Stack

#### Backend
- Python
- FastAPI
- LangGraph
- LangChain (LCEL)
- Qdrant
- Reranker / sentence-transformers
- OpenAI-compatible chat and embedding APIs

#### Frontend
- Next.js
- TypeScript
- React

#### Infra / Ops
- Docker
- GitHub Actions CI
- Cloud deployment workflow support
