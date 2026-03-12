import asyncio
from functools import partial
from sentence_transformers import CrossEncoder

class MiniLMReranker:
    def __init__(self):
        self.model = None
        self._logged_unavailable = False
        self.status = "lazy"
        print("---RERANKER INITIALIZED IN LAZY MODE---")

    def _get_model(self):
        if self.model is None:
            # Load lazily so the API can start even if the model is not cached yet.
            print("---LOADING RERANKER MODEL: cross-encoder/ms-marco-MiniLM-L-6-v2---")
            self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
            self.status = "active"
            print("---RERANKER ACTIVE---")
        return self.model

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

        try:
            model = await loop.run_in_executor(None, self._get_model)

            # We use partial to pass arguments to the model.predict function
            predict_func = partial(model.predict, pairs)
            scores = await loop.run_in_executor(None, predict_func)
        except Exception:
            # Fall back to original retrieval order if the reranker model is unavailable.
            self.status = "inactive"
            if not self._logged_unavailable:
                print("---RERANKER INACTIVE: FALLING BACK TO RETRIEVAL ORDER---")
                self._logged_unavailable = True
            return docs

        # 3. Attach scores & sort
        scored = list(zip(docs, scores))
        scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)

        reranked_docs = [doc for doc, score in scored_sorted]
        return reranked_docs
