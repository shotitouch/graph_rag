# graph/nodes.py
from typing import Any, Dict
import asyncio
import time
from core.retriever import get_reranked_docs
from core.chain import AnalyzeTenQQuery, get_chain, get_rewrite_chain, get_grader_chain, get_hallucination_chain, get_answer_grader_chain, get_query_analysis_chain, get_router_chain
from .state import AgentState
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from core.llm import llm
from utils.logger import get_logger

logger = get_logger(__name__)

QUESTION_TYPES = {
    "fact_lookup",
    "metric_lookup",
    "performance_summary",
    "risk_or_disclosure",
    "general_technical",
}

SCOPE_TYPES = {
    "current_filing",
    "single_company",
    "multi_company_comparison",
    "market_wide",
    "aggregate",
    "unknown",
}

def get_trace_fields(state: AgentState) -> tuple[str, str]:
    return state.get("thread_id", "unknown"), state.get("request_id", "unknown")

def duration_ms(start_time: float) -> float:
    return round((time.perf_counter() - start_time) * 1000, 2)

def build_source_entry(index: int, document) -> dict[str, Any]:
    source = document.metadata.get("file") or document.metadata.get("source") or "unknown"
    page = document.metadata.get("page")
    chunk_id = document.metadata.get("chunk_id")

    return {
        "id": f"S{index}",
        "source": source,
        "page": page,
        "chunk_id": chunk_id,
    }

def normalize_query_analysis_result(result: Any) -> dict[str, Any]:
    if isinstance(result, AnalyzeTenQQuery):
        data = result.model_dump()
    elif isinstance(result, dict):
        data = dict(result)
    else:
        raise TypeError(f"Unsupported query analysis result type: {type(result)!r}")

    question_type = str(data.get("question_type") or "general_technical")
    if question_type not in QUESTION_TYPES:
        question_type = "general_technical"

    scope_type = str(data.get("scope_type") or "unknown")
    if scope_type not in SCOPE_TYPES:
        scope_type = "unknown"

    query_tickers: list[str] = []
    for ticker in data.get("query_tickers") or []:
        if isinstance(ticker, str):
            cleaned = ticker.strip().upper()
            if cleaned and cleaned not in query_tickers:
                query_tickers.append(cleaned)

    query_year = data.get("query_year")
    if not isinstance(query_year, int):
        query_year = None

    query_period = data.get("query_period")
    if query_period not in {"Q1", "Q2", "Q3"}:
        query_period = None

    focus_terms: list[str] = []
    seen_terms: set[str] = set()
    for term in data.get("focus_terms") or []:
        if isinstance(term, str):
            cleaned = term.strip()
            lowered = cleaned.lower()
            if cleaned and lowered not in seen_terms:
                focus_terms.append(cleaned)
                seen_terms.add(lowered)

    return {
        "question_type": question_type,
        "scope_type": scope_type,
        "query_tickers": query_tickers,
        "query_year": query_year,
        "query_period": query_period or "",
        "multi_question": bool(data.get("multi_question", False)),
        "focus_terms": focus_terms[:6],
    }

async def router_node(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=route_intent thread_id=%s request_id=%s", thread_id, request_id)
    
    router_chain = get_router_chain()
    res = await router_chain.ainvoke({"question": question})
    # Using the robust extraction logic
    if isinstance(res, dict):
        decision = res.get("datasource", "technical")
    else:
        decision = getattr(res, "datasource", "technical")
    
    if decision not in ["conversational", "technical"]:
        decision = "technical"
        
    logger.info("event=node_completed node=route_intent thread_id=%s request_id=%s intent=%s duration_ms=%s", thread_id, request_id, decision, duration_ms(start_time))
    return {"intent": decision}

async def analyze_query_node(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=analyze_query thread_id=%s request_id=%s", thread_id, request_id)

    analyzer = get_query_analysis_chain()
    result = await analyzer.ainvoke({"question": question})
    normalized = normalize_query_analysis_result(result)

    logger.info(
        "event=node_completed node=analyze_query thread_id=%s request_id=%s question_type=%s scope_type=%s tickers=%s multi_question=%s duration_ms=%s",
        thread_id,
        request_id,
        normalized["question_type"],
        normalized["scope_type"],
        ",".join(normalized["query_tickers"]),
        normalized["multi_question"],
        duration_ms(start_time),
    )
    return normalized

def get_binary_score(res) -> str:
    """Extracts binary_score safely from an LLM response."""
    if res is None:
        return "no"
    
    if isinstance(res, dict):
        return str(res.get("binary_score", "no")).lower()
    
    return str(getattr(res, "binary_score", "no")).lower()

async def grade_documents_node(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    documents = state["documents"]
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=grade_docs thread_id=%s request_id=%s docs_count=%s", thread_id, request_id, len(documents))
    grader_chain = get_grader_chain()

    try:
        tasks = [
            grader_chain.ainvoke({ "question": question, "context": doc.page_content}) for doc in documents
        ]

        resList = await asyncio.gather(*tasks)

        relevant_docs = [
            doc for doc, res in zip(documents, resList) if get_binary_score(res) == 'yes'
        ]

        # Return the filtered list of documents
        logger.info("event=node_completed node=grade_docs thread_id=%s request_id=%s docs_in=%s relevant_docs=%s duration_ms=%s", thread_id, request_id, len(documents), len(relevant_docs), duration_ms(start_time))
        return {"documents": relevant_docs}
    
    except Exception as e:
        logger.exception("event=node_failed node=grade_docs thread_id=%s request_id=%s duration_ms=%s", thread_id, request_id, duration_ms(start_time))
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        raise e

async def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 1: Retrieve and Rerank documents.
    Uses the logic from retriever.py.
    """
    question = state["question"]
    messages = state.get("messages", [])
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=retrieve thread_id=%s request_id=%s", thread_id, request_id)

    updates = {}

    if not messages or messages[-1].type == "ai":
        updates["messages"] = [HumanMessage(content=question)]
    
    # Use your existing reranking logic
    documents = await get_reranked_docs(question)
    updates["documents"] = documents
    logger.info("event=node_completed node=retrieve thread_id=%s request_id=%s docs_count=%s duration_ms=%s", thread_id, request_id, len(documents), duration_ms(start_time))

    return updates

async def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 2: Generate an answer using the retrieved context.
    Uses the logic from chain.py and prompt.py.
    """
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=generate thread_id=%s request_id=%s", thread_id, request_id)

    try:
        question = state.get("question")
        documents = state.get("documents", [])
        full_history = state.get("messages", [])
        trimmed_history = trimmed_history = full_history[-6:] if full_history else [] # simple limit history len, reduce memory usage
        # Build stable source IDs so the answer and API payload reference the same evidence.
        context_chunks = []
        sources = []
        for index, d in enumerate(documents, start=1):
            source_entry = build_source_entry(index, d)
            sources.append(source_entry)
            citation_tag = f"[{source_entry['id']}: {source_entry['source']}, page {source_entry['page']}]"
            context_chunks.append(f"{citation_tag}\n{d.page_content}")
        
        formatted_context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No documents found. Answer conversationally."

        # Run your existing chain
        chain = get_chain()
        generation = await chain.ainvoke({
            "history": trimmed_history,
            "question": question,
            "context": formatted_context
        })

        logger.info("event=node_completed node=generate thread_id=%s request_id=%s sources_count=%s duration_ms=%s", thread_id, request_id, len(sources), duration_ms(start_time))
        return {
            "messages": [AIMessage(content=generation)], 
            "generation": generation,
            "sources": sources,
        }
    except Exception as e:
        logger.exception("event=node_failed node=generate thread_id=%s request_id=%s duration_ms=%s", thread_id, request_id, duration_ms(start_time))
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        raise e


async def rewrite_node(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    history = state.get("messages", [])
    current_retry = state.get("retry_count", 0)
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    is_grounded = state.get("is_grounded")
    is_useful = state.get("is_useful")
    documents = state.get("documents", [])

    reason = "The initial search didn't find relevant documents."
    if documents and is_grounded == "no":
        reason = "The previous answer was a hallucination; it wasn't supported by the facts found."
    elif documents and is_useful == "no":
        reason = "The previous answer didn't sufficiently answer the user's specific question."
    logger.warning("event=node_started node=rewrite thread_id=%s request_id=%s retry_count=%s reason=%s", thread_id, request_id, current_retry, reason)

    # 1. The Rewrite Logic
    rewriter = get_rewrite_chain()
    better_question = await rewriter.ainvoke({
        "history": history,
        "question": question,
        "reason": reason
    })

    logger.info("event=node_completed node=rewrite thread_id=%s request_id=%s retry_count=%s duration_ms=%s", thread_id, request_id, current_retry + 1, duration_ms(start_time))

    # 2. Return the new question AND increment the retry count
    return {
        "question": better_question, 
        "retry_count": state.get("retry_count", 0) + 1,
        # THE CLEANING PART:
        "generation": "",      # Erase the old answer
        "is_grounded": "",     # Erase the old grade
        "is_useful": "",       # Erase the old grade
        "documents": [],       # Clear old docs so we don't reuse them
        "sources": []
    }



async def hallucination_grader_node(state: AgentState) -> Dict[str, Any]:
    generation = state["generation"]
    documents = state["documents"]
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=grade_hallucination thread_id=%s request_id=%s docs_count=%s", thread_id, request_id, len(documents))

    if not documents:
        logger.warning("event=node_completed node=grade_hallucination thread_id=%s request_id=%s outcome=skipped_no_documents duration_ms=%s", thread_id, request_id, duration_ms(start_time))
        return {"is_grounded": "yes"}
    
    # 1. Prepare the context
    context = "\n\n".join([d.page_content for d in documents])
    
    # 2. Run the Grader Chain
    # Note: You'll need to define get_hallucination_chain in your core/chain.py
    grader_chain = get_hallucination_chain()
    res = await grader_chain.ainvoke({
        "documents": context, 
        "generation": generation
    })

    score = get_binary_score(res)


    logger.info("event=node_completed node=grade_hallucination thread_id=%s request_id=%s grounded=%s duration_ms=%s", thread_id, request_id, score.lower(), duration_ms(start_time))
    return {"is_grounded": score.lower()}

async def answer_grader_node(state: AgentState) -> Dict[str, Any]:
    generation = state["generation"]
    question = state["question"]
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=grade_answer thread_id=%s request_id=%s", thread_id, request_id)

    if not generation or not question:
        logger.warning("event=node_completed node=grade_answer thread_id=%s request_id=%s outcome=missing_generation duration_ms=%s", thread_id, request_id, duration_ms(start_time))
        return {"is_useful": "no", "documents": []}
    
    try:
        grader_chain = get_answer_grader_chain()
        res = await grader_chain.ainvoke({
            "question": question, 
            "generation": generation
        })

        score = get_binary_score(res)

        logger.info("event=node_completed node=grade_answer thread_id=%s request_id=%s useful=%s duration_ms=%s", thread_id, request_id, score, duration_ms(start_time))
        return {
            "is_useful": score,
            "documents": [] # memory cleanup
        }

    except Exception as e:
        logger.exception("event=node_failed node=grade_answer thread_id=%s request_id=%s duration_ms=%s", thread_id, request_id, duration_ms(start_time))
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        return {"is_useful": "no", "documents": []}
