from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from core.embeddings import embeddings
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
from core.reranker import MiniLMReranker
from utils.logger import get_logger

logger = get_logger(__name__)

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def _collection_exists(collection_name: str) -> bool:
    existing_collections = {
        collection.name for collection in qdrant_client.get_collections().collections
    }
    return collection_name in existing_collections


def ensure_qdrant_collection() -> None:
    if _collection_exists(QDRANT_COLLECTION):
        return

    logger.info(
        "event=qdrant_collection_create_started collection=%s",
        QDRANT_COLLECTION,
    )
    embedding_dimension = len(embeddings.embed_query("dimension probe"))

    try:
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=embedding_dimension,
                distance=Distance.COSINE,
            ),
        )
    except Exception:
        if not _collection_exists(QDRANT_COLLECTION):
            logger.exception(
                "event=qdrant_collection_create_failed collection=%s",
                QDRANT_COLLECTION,
            )
            raise
    else:
        logger.info(
            "event=qdrant_collection_create_completed collection=%s size=%s",
            QDRANT_COLLECTION,
            embedding_dimension,
        )

vectorstore = QdrantVectorStore(
    client=qdrant_client,
    collection_name=QDRANT_COLLECTION,
    embedding=embeddings,
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
