from .state import AgentState
from shared.logging import get_logger

logger = get_logger(__name__)

ALLOWED_COVERAGE_TYPES = {
    "default_technical",
    "focused_lookup",
    "retrieval_heavy",
    "token_heavy",
    "computation_heavy",
}
SUPPORTED_SPECIALIZED_SCOPES = {"current_filing", "single_company"}

def get_trace_fields(state: AgentState) -> tuple[str, str]:
    return state.get("thread_id", "unknown"), state.get("request_id", "unknown")

def resolve_coverage_type(state: AgentState) -> str:
    coverage_type = state.get("coverage_type", "default_technical")
    scope_type = state.get("scope_type", "unknown")
    query_tickers = state.get("query_tickers", [])
    multi_question = bool(state.get("multi_question", False))

    if coverage_type not in ALLOWED_COVERAGE_TYPES:
        return "default_technical"

    if coverage_type == "default_technical":
        return coverage_type

    if multi_question:
        return "default_technical"

    if len(query_tickers) > 1:
        return "default_technical"

    if scope_type not in SUPPORTED_SPECIALIZED_SCOPES:
        return "default_technical"

    return coverage_type

def route_based_on_intent(state: AgentState):
    """
    Looks at the intent stored in state and decides 
    whether to go to the RAG path or the Chat path.
    """
    intent = state.get("intent")
    thread_id, request_id = get_trace_fields(state)
    
    if intent == "conversational":
        logger.info("event=route_decision route=conversational thread_id=%s request_id=%s", thread_id, request_id)
        return "conversational"
    
    # Default to technical if something goes wrong or it's classified as such
    logger.info("event=route_decision route=technical thread_id=%s request_id=%s", thread_id, request_id)
    return "technical"

def route_technical_coverage(state: AgentState):
    thread_id, request_id = get_trace_fields(state)
    resolved = resolve_coverage_type(state)
    requested = state.get("coverage_type", "default_technical")
    logger.info(
        "event=coverage_route_decision requested=%s resolved=%s scope_type=%s multi_question=%s thread_id=%s request_id=%s",
        requested,
        resolved,
        state.get("scope_type", "unknown"),
        bool(state.get("multi_question", False)),
        thread_id,
        request_id,
    )
    return resolved

def route_after_generate(state: AgentState):
    intent = state.get("intent")
    thread_id, request_id = get_trace_fields(state)
    
    if intent == "conversational":
        logger.info("event=post_generate_route route=conversational thread_id=%s request_id=%s", thread_id, request_id)
        return "conversational"
    
    # Default to technical if something goes wrong or it's classified as such
    logger.info("event=post_generate_route route=technical thread_id=%s request_id=%s", thread_id, request_id)
    return "technical"

def doc_grader(state: AgentState):
    """
    Determines whether to generate an answer, rewrite the query, or exit.
    """
    documents = state.get("documents", [])
    retry_count = state.get("retry_count", 0)
    thread_id, request_id = get_trace_fields(state)

    # 1. If we found documents, move to generation
    if documents:
        logger.info("event=doc_grader_decision outcome=useful thread_id=%s request_id=%s retry_count=%s docs_count=%s", thread_id, request_id, retry_count, len(documents))
        return "useful"

    # 2. Safety Break: If no docs found, check if we've exhausted retries
    if retry_count >= 3:
        logger.warning("event=doc_grader_retry_exhausted outcome=useful thread_id=%s request_id=%s retry_count=%s docs_count=0", thread_id, request_id, retry_count)
        # You can route to "generate" anyway to have the LLM say "I don't know"
        # or route to a specific 'failure' node.
        return "useful" 

    # 3. If no docs and we still have retries left, rewrite
    logger.warning("event=doc_grader_decision outcome=not_useful thread_id=%s request_id=%s retry_count=%s docs_count=0", thread_id, request_id, retry_count)
    return "not_useful"

def route_after_doc_grading(state: AgentState):
    documents = state.get("documents", [])
    retry_count = state.get("retry_count", 0)
    coverage_type = resolve_coverage_type(state)
    thread_id, request_id = get_trace_fields(state)

    if not documents:
        if retry_count >= 3:
            logger.warning(
                "event=doc_route_decision outcome=generate_fallback thread_id=%s request_id=%s retry_count=%s docs_count=0",
                thread_id,
                request_id,
                retry_count,
            )
            return "generate"

        logger.warning(
            "event=doc_route_decision outcome=rewrite thread_id=%s request_id=%s retry_count=%s docs_count=0",
            thread_id,
            request_id,
            retry_count,
        )
        return "rewrite"

    if coverage_type == "retrieval_heavy":
        next_step = "prepare_retrieval_heavy_context"
    elif coverage_type == "token_heavy":
        next_step = "prepare_token_heavy_context"
    elif coverage_type == "computation_heavy":
        next_step = "prepare_computation_context"
    else:
        next_step = "generate"

    logger.info(
        "event=doc_route_decision outcome=%s thread_id=%s request_id=%s retry_count=%s docs_count=%s",
        next_step,
        thread_id,
        request_id,
        retry_count,
        len(documents),
    )
    return next_step

def check_hallucination(state: AgentState):
    is_grounded = state.get("is_grounded") == "yes"
    retry_count = state.get("retry_count", 0)
    thread_id, request_id = get_trace_fields(state)

    if is_grounded:
        logger.info("event=hallucination_gate outcome=grounded thread_id=%s request_id=%s retry_count=%s", thread_id, request_id, retry_count)
        return "grounded"
    
    # If it's a hallucination ('no') and we have retries left
    if not is_grounded and retry_count < 3:
        logger.warning("event=hallucination_gate outcome=hallucinated thread_id=%s request_id=%s retry_count=%s", thread_id, request_id, retry_count)
        return "hallucinated"
    
    # Final fallback: out of retries, just give the answer
    logger.warning("event=hallucination_gate outcome=grounded thread_id=%s request_id=%s retry_count=%s fallback=max_retries", thread_id, request_id, retry_count)
    return "grounded"

def answer_evaluator(state: AgentState):
    is_useful = state.get("is_useful") == "yes"
    retry_count = state.get("retry_count", 0)
    thread_id, request_id = get_trace_fields(state)

    if is_useful:
        logger.info("event=answer_evaluator outcome=useful thread_id=%s request_id=%s retry_count=%s", thread_id, request_id, retry_count)
        return "useful"
    
    # If it's a hallucination ('no') and we have retries left
    if not is_useful and retry_count < 3:
        logger.warning("event=answer_evaluator outcome=not_useful thread_id=%s request_id=%s retry_count=%s", thread_id, request_id, retry_count)
        return "not_useful"
    
    # Final fallback: out of retries, just give the answer
    logger.warning("event=answer_evaluator outcome=useful thread_id=%s request_id=%s retry_count=%s fallback=max_retries", thread_id, request_id, retry_count)
    return "useful"
