from langchain_community.vectorstores import Chroma
from core.embeddings import embeddings
from config import PERSIST_DIR
from core.reranker import BGEReranker


vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 15})
reranker = BGEReranker()

async def get_reranked_docs(q):
    docs = await retriever.ainvoke(q)
    reranked_docs = await reranker.rerank(q, docs)

    return reranked_docs[:3]