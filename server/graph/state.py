from typing import List, TypedDict, Annotated, Optional
from langchain_core.documents import Document
from langgraph.graph.message import add_messages, AnyMessage

class AgentState(TypedDict):
    question: str
    intent: str
    # Annotated with add_messages makes this a "living" history list
    messages: Annotated[list[AnyMessage], add_messages]
    documents: List[Document]
    generation: str
    retry_count: int
    is_grounded: str  # 'yes' or 'no'
    is_useful: str    # 'yes' or 'no'