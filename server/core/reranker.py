# reranker.py
from sentence_transformers import CrossEncoder
import asyncio

class BGEReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model = CrossEncoder(model_name)

    async def rerank(self, query, docs):
        """
        docs: list of langchain Document objects
        returns: reranked list of Document
        """
        pairs = [[query, doc.page_content] for doc in docs]

        # Scores: higher = better
        # We offload the CPU-heavy .predict call to a separate thread.
        # This prevents the reranker from freezing FastAPI server.
        scores = await asyncio.to_thread(self.model.predict, pairs)

        # Attach scores & sort
        scored = list(zip(docs, scores))
        scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)

        reranked_docs = [doc for doc, score in scored_sorted]
        return reranked_docs
