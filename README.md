# 🕸️ Agentic Graph-Based PDF RAG

A high-performance, state-aware retrieval system that leverages **cyclic cognitive architectures** to handle complex document queries. This project moves beyond simple vector search by implementing autonomous loops to verify and refine answers.

## 🚀 Core Features
* [cite_start]**Two-Stage Retrieval:** Combines **ChromaDB** vector search with a **BGE-Reranker** to ensure the most relevant context is prioritized[cite: 9, 24].
* [cite_start]**Agentic Orchestration:** Utilizes **LangGraph** (LCEL) to manage stateful loops, allowing the system to self-correct if retrieved data is insufficient[cite: 9, 24].
* [cite_start]**Asynchronous Backend:** Powered by **FastAPI** to handle real-time streaming and high-concurrency document processing[cite: 24, 25].
* [cite_start]**Verifiable Citations:** Every response includes direct citations from the source PDF to ensure groundedness and prevent hallucinations[cite: 25].

## 🏗️ Technical Architecture
The system follows a "Corrective-RAG" (CRAG) pattern:
1. **Routing:** Incoming queries are analyzed to determine the best retrieval path.
2. **Retrieval & Grading:** Context is fetched and graded for relevance.
3. **Knowledge Refinement:** If the grade is low, the agent triggers a query-rewrite loop to find better context.
4. **Generation:** The LLM synthesizes a final answer only when the "groundedness" threshold is met.



## 🛠️ Stack
* [cite_start]**Orchestration:** LangGraph, LangChain [cite: 9]
* [cite_start]**Embeddings & Ranking:** BGE-Reranker, Transformers [cite: 8, 9, 24]
* [cite_start]**Vector Store:** ChromaDB [cite: 9, 24]
* [cite_start]**API:** FastAPI (Asynchronous) [cite: 10, 24]
* [cite_start]**Frontend:** Next.js with real-time streaming [cite: 20, 25]

## 📊 Performance & Optimization
[cite_start]The pipeline was optimized through fine-tuning and ablation studies, similar to the methodology used in my NLP research where I achieved a **0.9065 Micro F1** score by optimizing context capture[cite: 27, 28]. This project applies those same principles to ensure high-fidelity retrieval from multi-page PDFs.

---
[cite_start]**Maintained by [Shotitouch Tuangcharoentip](https://github.com/shotitouch)** *MS in Machine Learning, Stevens Institute of Technology (GPA: 4.0)* [cite: 1, 32]