from typing import Literal, TypedDict


class IngestResult(TypedDict):
    status: str
    message: str
    parent_id: str
    ticker: str
    year: int | None
    period: Literal["Q1", "Q2", "Q3"] | None
    mode: str
    metadata_complete: bool
    used_llm_fallback: bool
    chunks_added: int
