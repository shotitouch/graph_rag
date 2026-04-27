from typing import TypedDict


class SourceEntry(TypedDict):
    id: str
    source: str
    page: int | None
    chunk_id: str | None
