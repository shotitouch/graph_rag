from langchain_community.vectorstores import Chroma
from core.embeddings import embeddings
from config import PERSIST_DIR
from core.reranker import MiniLMReranker


vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) # reduce memory usage
reranker = MiniLMReranker()

async def get_reranked_docs(q):
    docs = await retriever.ainvoke(q)
    reranked_docs = await reranker.rerank(q, docs)

    final_docs = reranked_docs[:3]

    # reduce memory usage
    del docs
    del reranked_docs

    return final_docs