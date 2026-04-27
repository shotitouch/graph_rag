from typing import Any, List, TypedDict, Annotated
from langchain_core.documents import Document
from langgraph.graph.message import add_messages, AnyMessage
from shared.models import SourceEntry

class AgentState(TypedDict):
    question: str
    intent: str
    thread_id: str
    request_id: str
    # Annotated with add_messages makes this a "living" history list
    messages: Annotated[list[AnyMessage], add_messages]
    documents: List[Document]
    generation: str
    retry_count: int
    is_grounded: str  # 'yes' or 'no'
    is_useful: str    # 'yes' or 'no'
    sources: List[SourceEntry]
    question_type: str
    coverage_type: str
    scope_type: str
    query_tickers: List[str]
    query_year: int | None
    query_period: str
    multi_question: bool
    focus_terms: List[str]
    prepared_context: str
