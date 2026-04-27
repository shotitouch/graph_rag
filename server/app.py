import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ask.router import router as ask_router
from health.router import router as health_router
from ingestion.router import router as ingest_router
from retrieval.service import ensure_qdrant_collection, get_retriever, reranker
from shared.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Agentic RAG", version="1.0.0")
logger.info("event=api_startup status=initialized version=1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",  # allow all during development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ask_router)
app.include_router(health_router)
app.include_router(ingest_router)

@app.on_event("startup")
async def preload_models():
    logger.info("event=startup_preload component=qdrant_collection status=starting")
    ensure_qdrant_collection()
    logger.info("event=startup_preload component=qdrant_collection status=ready")
    logger.info("event=startup_preload component=retriever status=starting")
    get_retriever()
    logger.info("event=startup_preload component=retriever status=ready")
    logger.info("event=startup_preload component=reranker status=starting")
    reranker.preload()
    logger.info("event=startup_preload component=reranker status=%s", reranker.status.lower())

@app.get("/")
def home():
    return {"message": "Agentic RAG API running"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
