from typing import TypedDict


class RetrievedDocumentMetadata(TypedDict, total=False):
    parent_id: str
    ticker: str
    year: int | None
    period: str | None
    filing_type: str
    ingest_mode: str
    metadata_complete: bool
    source: str
    page: int | None
    chunk_id: str
    content_type: str
    type: str
