from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    VectorParams,
)

from llm_runtime.client import embeddings
from retrieval.reranker import MiniLMReranker
from shared.config import QDRANT_API_KEY, QDRANT_COLLECTION, QDRANT_URL
from shared.logging import get_logger

logger = get_logger(__name__)

qdrant_client: QdrantClient | None = None
vectorstore: QdrantVectorStore | None = None
retriever = None


def get_qdrant_client() -> QdrantClient:
    global qdrant_client

    if qdrant_client is None:
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

    return qdrant_client


def get_vectorstore() -> QdrantVectorStore:
    global vectorstore

    if vectorstore is None:
        vectorstore = QdrantVectorStore(
            client=get_qdrant_client(),
            collection_name=QDRANT_COLLECTION,
            embedding=embeddings,
        )

    return vectorstore


def get_retriever():
    global retriever

    if retriever is None:
        retriever = get_vectorstore().as_retriever(search_kwargs={"k": 5})

    return retriever


def build_qdrant_filter(
    *,
    tickers: list[str] | None = None,
    year: int | None = None,
    period: str | None = None,
) -> Filter | None:
    conditions: list[FieldCondition] = []

    cleaned_tickers = []
    for ticker in tickers or []:
        if isinstance(ticker, str):
            cleaned = ticker.strip().upper()
            if cleaned and cleaned not in cleaned_tickers:
                cleaned_tickers.append(cleaned)

    if len(cleaned_tickers) == 1:
        conditions.append(
            FieldCondition(
                key="metadata.ticker",
                match=MatchValue(value=cleaned_tickers[0]),
            )
        )
    elif cleaned_tickers:
        conditions.append(
            FieldCondition(
                key="metadata.ticker",
                match=MatchAny(any=cleaned_tickers),
            )
        )

    if isinstance(year, int):
        conditions.append(
            FieldCondition(
                key="metadata.year",
                match=MatchValue(value=year),
            )
        )

    if period in {"Q1", "Q2", "Q3"}:
        conditions.append(
            FieldCondition(
                key="metadata.period",
                match=MatchValue(value=period),
            )
        )

    if not conditions:
        return None

    return Filter(must=conditions)


def _collection_exists(collection_name: str) -> bool:
    existing_collections = {
        collection.name for collection in get_qdrant_client().get_collections().collections
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
        get_qdrant_client().create_collection(
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


reranker = MiniLMReranker()

async def get_reranked_docs(
    q: str,
    *,
    tickers: list[str] | None = None,
    year: int | None = None,
    period: str | None = None,
    candidate_k: int = 5,
    final_k: int = 3,
):
    normalized_tickers = sorted(
        {
            ticker.strip().upper()
            for ticker in tickers or []
            if isinstance(ticker, str) and ticker.strip()
        }
    )
    qdrant_filter = build_qdrant_filter(
        tickers=normalized_tickers,
        year=year,
        period=period,
    )

    docs = await get_vectorstore().asimilarity_search(
        q,
        k=candidate_k,
        filter=qdrant_filter,
    )
    logger.info(
        "event=retrieval_completed docs_count=%s candidate_k=%s filter_active=%s tickers=%s year=%s period=%s",
        len(docs),
        candidate_k,
        qdrant_filter is not None,
        ",".join(normalized_tickers),
        year,
        period or "",
    )

    reranked_docs = await reranker.rerank(q, docs)
    logger.info("event=reranker_completed status=%s", reranker.status.lower())

    final_docs = reranked_docs[:final_k]
    logger.info("event=rerank_returning docs_count=%s final_k=%s", len(final_docs), final_k)

    # reduce memory usage
    del docs
    del reranked_docs

    return final_docs
