import uvicorn
from fastapi import FastAPI
from router.ask import router as ask_router
from router.health import router as health_router
from router.ingest import router as ingest_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Agentic RAG", version="1.0.0")

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

@app.get("/")
def home():
    return {"message": "Agentic RAG API running"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)