# workflow/nodes.py
from typing import Any, Dict
import asyncio
import time

from langchain_core.messages import AIMessage, HumanMessage

from llm_runtime.chains import (
    AnalyzeTenQQuery,
    ComputationExtraction,
    get_answer_grader_chain,
    get_chain,
    get_computation_extraction_chain,
    get_context_compression_chain,
    get_grader_chain,
    get_hallucination_chain,
    get_query_analysis_chain,
    get_rewrite_chain,
    get_router_chain,
)
from retrieval.service import get_reranked_docs
from shared.logging import get_logger
from shared.models import SourceEntry

from .state import AgentState

logger = get_logger(__name__)

QUESTION_TYPES = {
    "fact_lookup",
    "metric_lookup",
    "performance_summary",
    "risk_or_disclosure",
    "general_technical",
}

COVERAGE_TYPES = {
    "default_technical",
    "focused_lookup",
    "retrieval_heavy",
    "token_heavy",
    "computation_heavy",
}

SCOPE_TYPES = {
    "current_filing",
    "single_company",
    "multi_company_comparison",
    "market_wide",
    "aggregate",
    "unknown",
}

RETRIEVAL_PROFILES = {
    "default_technical": {"candidate_k": 5, "final_k": 3},
    "focused_lookup": {"candidate_k": 4, "final_k": 3},
    "retrieval_heavy": {"candidate_k": 8, "final_k": 5},
    "token_heavy": {"candidate_k": 10, "final_k": 6},
    "computation_heavy": {"candidate_k": 8, "final_k": 4},
}

def get_trace_fields(state: AgentState) -> tuple[str, str]:
    return state.get("thread_id", "unknown"), state.get("request_id", "unknown")

def duration_ms(start_time: float) -> float:
    return round((time.perf_counter() - start_time) * 1000, 2)

def build_source_entry(index: int, document) -> SourceEntry:
    source = document.metadata.get("file") or document.metadata.get("source") or "unknown"
    page = document.metadata.get("page")
    chunk_id = document.metadata.get("chunk_id")

    return {
        "id": f"S{index}",
        "source": source,
        "page": page,
        "chunk_id": chunk_id,
    }

def format_documents_for_context(documents) -> tuple[str, list[SourceEntry]]:
    context_chunks = []
    sources = []

    for index, document in enumerate(documents, start=1):
        source_entry = build_source_entry(index, document)
        sources.append(source_entry)
        citation_tag = f"[{source_entry['id']}: {source_entry['source']}, page {source_entry['page']}]"
        context_chunks.append(f"{citation_tag}\n{document.page_content}")

    formatted_context = (
        "\n\n---\n\n".join(context_chunks) if context_chunks else "No documents found. Answer conversationally."
    )
    return formatted_context, sources

def format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")

def compute_deterministic_result(result: ComputationExtraction) -> tuple[float, str] | None:
    facts = result.facts
    operation = result.operation

    if operation == "unsupported":
        return None

    if operation in {"difference", "ratio", "percentage_of_total", "percentage_change"} and len(facts) < 2:
        return None

    if operation == "sum" and not facts:
        return None

    if operation == "difference":
        computed_value = facts[0].value - facts[1].value
    elif operation == "ratio":
        if facts[1].value == 0:
            return None
        computed_value = facts[0].value / facts[1].value
    elif operation == "percentage_of_total":
        if facts[1].value == 0:
            return None
        computed_value = (facts[0].value / facts[1].value) * 100
    elif operation == "percentage_change":
        if facts[0].value == 0:
            return None
        computed_value = ((facts[1].value - facts[0].value) / facts[0].value) * 100
    elif operation == "sum":
        computed_value = sum(fact.value for fact in facts)
    else:
        return None

    display_unit = result.result_unit or ""
    if operation in {"percentage_change", "percentage_of_total"} and not display_unit:
        display_unit = "%"
    return computed_value, display_unit

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

    coverage_type = str(data.get("coverage_type") or "default_technical")
    if coverage_type not in COVERAGE_TYPES:
        coverage_type = "default_technical"

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
        "coverage_type": coverage_type,
        "scope_type": scope_type,
        "query_tickers": query_tickers,
        "query_year": query_year,
        "query_period": query_period or "",
        "multi_question": bool(data.get("multi_question", False)),
        "focus_terms": focus_terms[:6],
        "prepared_context": "",
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
        "event=node_completed node=analyze_query thread_id=%s request_id=%s question_type=%s coverage_type=%s scope_type=%s tickers=%s multi_question=%s duration_ms=%s",
        thread_id,
        request_id,
        normalized["question_type"],
        normalized["coverage_type"],
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

async def run_retrieve_with_profile(
    state: AgentState,
    *,
    profile_name: str,
) -> Dict[str, Any]:
    question = state["question"]
    messages = state.get("messages", [])
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    profile = RETRIEVAL_PROFILES[profile_name]
    logger.info(
        "event=node_started node=retrieve thread_id=%s request_id=%s profile=%s candidate_k=%s final_k=%s",
        thread_id,
        request_id,
        profile_name,
        profile["candidate_k"],
        profile["final_k"],
    )

    updates = {}

    if not messages or messages[-1].type == "ai":
        updates["messages"] = [HumanMessage(content=question)]

    documents = await get_reranked_docs(
        question,
        tickers=state.get("query_tickers", []),
        year=state.get("query_year"),
        period=state.get("query_period") or None,
        candidate_k=profile["candidate_k"],
        final_k=profile["final_k"],
    )
    updates["documents"] = documents
    updates["prepared_context"] = ""
    logger.info(
        "event=node_completed node=retrieve thread_id=%s request_id=%s profile=%s docs_count=%s duration_ms=%s",
        thread_id,
        request_id,
        profile_name,
        len(documents),
        duration_ms(start_time),
    )

    return updates

async def retrieve_node(state: AgentState) -> Dict[str, Any]:
    return await run_retrieve_with_profile(state, profile_name="default_technical")

async def retrieve_focused_lookup_node(state: AgentState) -> Dict[str, Any]:
    return await run_retrieve_with_profile(state, profile_name="focused_lookup")

async def retrieve_retrieval_heavy_node(state: AgentState) -> Dict[str, Any]:
    return await run_retrieve_with_profile(state, profile_name="retrieval_heavy")

async def retrieve_token_heavy_node(state: AgentState) -> Dict[str, Any]:
    return await run_retrieve_with_profile(state, profile_name="token_heavy")

async def retrieve_computation_heavy_node(state: AgentState) -> Dict[str, Any]:
    return await run_retrieve_with_profile(state, profile_name="computation_heavy")

async def prepare_retrieval_heavy_context_node(state: AgentState) -> Dict[str, Any]:
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    documents = state.get("documents", [])
    logger.info(
        "event=node_started node=prepare_retrieval_heavy_context thread_id=%s request_id=%s docs_count=%s",
        thread_id,
        request_id,
        len(documents),
    )

    formatted_context, _ = format_documents_for_context(documents)
    prepared_context = (
        "Evidence gathered from multiple relevant passages in the same filing:\n"
        f"{formatted_context}"
    )

    logger.info(
        "event=node_completed node=prepare_retrieval_heavy_context thread_id=%s request_id=%s duration_ms=%s",
        thread_id,
        request_id,
        duration_ms(start_time),
    )
    return {"prepared_context": prepared_context}

async def prepare_token_heavy_context_node(state: AgentState) -> Dict[str, Any]:
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    documents = state.get("documents", [])
    logger.info(
        "event=node_started node=prepare_token_heavy_context thread_id=%s request_id=%s docs_count=%s",
        thread_id,
        request_id,
        len(documents),
    )

    formatted_context, _ = format_documents_for_context(documents)
    compressor = get_context_compression_chain()
    prepared_context = await compressor.ainvoke({
        "question": state.get("question", ""),
        "context": formatted_context,
    })

    logger.info(
        "event=node_completed node=prepare_token_heavy_context thread_id=%s request_id=%s duration_ms=%s",
        thread_id,
        request_id,
        duration_ms(start_time),
    )
    return {"prepared_context": prepared_context}

async def prepare_computation_context_node(state: AgentState) -> Dict[str, Any]:
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    documents = state.get("documents", [])
    logger.info(
        "event=node_started node=prepare_computation_context thread_id=%s request_id=%s docs_count=%s",
        thread_id,
        request_id,
        len(documents),
    )

    formatted_context, _ = format_documents_for_context(documents)
    extractor = get_computation_extraction_chain()
    extraction = await extractor.ainvoke({
        "question": state.get("question", ""),
        "context": formatted_context,
    })
    if isinstance(extraction, dict):
        extraction = ComputationExtraction.model_validate(extraction)

    computed = compute_deterministic_result(extraction)
    if computed is None:
        logger.warning(
            "event=node_completed node=prepare_computation_context thread_id=%s request_id=%s outcome=fallback_default duration_ms=%s",
            thread_id,
            request_id,
            duration_ms(start_time),
        )
        return {"coverage_type": "default_technical", "prepared_context": ""}

    computed_value, display_unit = computed
    fact_lines = []
    for fact in extraction.facts:
        unit_suffix = f" {fact.unit}".rstrip()
        fact_lines.append(
            f"- [{fact.citation_id}] {fact.label}: {format_number(fact.value)}{unit_suffix}"
        )

    result_value = format_number(computed_value)
    result_suffix = f" {display_unit}".rstrip()
    prepared_context = (
        "Deterministic calculation prepared from filing evidence:\n"
        f"- Result label: {extraction.result_label}\n"
        f"- Computed result: {result_value}{result_suffix}\n"
        "- Supporting facts:\n"
        f"{chr(10).join(fact_lines)}"
    )

    logger.info(
        "event=node_completed node=prepare_computation_context thread_id=%s request_id=%s operation=%s facts_count=%s duration_ms=%s",
        thread_id,
        request_id,
        extraction.operation,
        len(extraction.facts),
        duration_ms(start_time),
    )
    return {
        "prepared_context": prepared_context,
        "coverage_type": "computation_heavy",
    }

async def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 2: Generate an answer using the retrieved context.
    Uses the llm runtime chains and prompts.
    """
    thread_id, request_id = get_trace_fields(state)
    start_time = time.perf_counter()
    logger.info("event=node_started node=generate thread_id=%s request_id=%s", thread_id, request_id)

    try:
        question = state.get("question")
        documents = state.get("documents", [])
        prepared_context = (state.get("prepared_context") or "").strip()
        full_history = state.get("messages", [])
        trimmed_history = full_history[-6:] if full_history else []
        formatted_context, sources = format_documents_for_context(documents)
        context_for_generation = prepared_context or formatted_context

        # Run your existing chain
        chain = get_chain()
        generation = await chain.ainvoke({
            "history": trimmed_history,
            "question": question,
            "context": context_for_generation
        })

        logger.info(
            "event=node_completed node=generate thread_id=%s request_id=%s coverage_type=%s used_prepared_context=%s sources_count=%s duration_ms=%s",
            thread_id,
            request_id,
            state.get("coverage_type", "default_technical"),
            bool(prepared_context),
            len(sources),
            duration_ms(start_time),
        )
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
        "sources": [],
        "prepared_context": "",
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
