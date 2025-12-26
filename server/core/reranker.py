import asyncio
from functools import partial
from sentence_transformers import CrossEncoder

class MiniLMReranker:
    def __init__(self):
        # Initializing on CPU as per your original code
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device='cpu')

    async def rerank(self, query, docs):
        """
        docs: list of langchain Document objects
        returns: reranked list of Document (asynchronously)
        """
        if not docs:
            return []

        # 1. Prepare pairs
        pairs = [(query, doc.page_content) for doc in docs]

        # 2. Run CPU-bound prediction in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        
        # We use partial to pass arguments to the model.predict function
        predict_func = partial(self.model.predict, pairs)
        scores = await loop.run_in_executor(None, predict_func)

        # 3. Attach scores & sort
        scored = list(zip(docs, scores))
        scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)

        reranked_docs = [doc for doc, score in scored_sorted]
        return reranked_docs