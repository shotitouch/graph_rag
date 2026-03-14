from langchain_community.vectorstores import Chroma
from core.embeddings import embeddings
from config import PERSIST_DIR
from core.reranker import MiniLMReranker
from utils.logger import get_logger

logger = get_logger(__name__)

vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) # reduce memory usage
reranker = MiniLMReranker()

async def get_reranked_docs(q):
    docs = await retriever.ainvoke(q)
    logger.info("event=retrieval_completed docs_count=%s", len(docs))

    reranked_docs = await reranker.rerank(q, docs)
    logger.info("event=reranker_completed status=%s", reranker.status.lower())

    final_docs = reranked_docs[:3]
    logger.info("event=rerank_returning docs_count=%s", len(final_docs))

    # reduce memory usage
    del docs
    del reranked_docs

    return final_docs
