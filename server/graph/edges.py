from .state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)

def route_based_on_intent(state: AgentState):
    """
    Looks at the intent stored in state and decides 
    whether to go to the RAG path or the Chat path.
    """
    intent = state.get("intent")
    
    if intent == "conversational":
        logger.info("event=route_decision route=conversational")
        return "conversational"
    
    # Default to technical if something goes wrong or it's classified as such
    logger.info("event=route_decision route=technical")
    return "technical"

def route_after_generate(state: AgentState):
    intent = state.get("intent")
    
    if intent == "conversational":
        logger.info("event=post_generate_route route=conversational")
        return "conversational"
    
    # Default to technical if something goes wrong or it's classified as such
    logger.info("event=post_generate_route route=technical")
    return "technical"

def doc_grader(state: AgentState):
    """
    Determines whether to generate an answer, rewrite the query, or exit.
    """
    documents = state.get("documents", [])
    retry_count = state.get("retry_count", 0)

    # 1. If we found documents, move to generation
    if documents:
        logger.info("event=doc_grader_decision outcome=useful retry_count=%s docs_count=%s", retry_count, len(documents))
        return "useful"

    # 2. Safety Break: If no docs found, check if we've exhausted retries
    if retry_count >= 3:
        logger.warning("event=doc_grader_retry_exhausted outcome=useful retry_count=%s docs_count=0", retry_count)
        # You can route to "generate" anyway to have the LLM say "I don't know"
        # or route to a specific 'failure' node.
        return "useful" 

    # 3. If no docs and we still have retries left, rewrite
    logger.warning("event=doc_grader_decision outcome=not_useful retry_count=%s docs_count=0", retry_count)
    return "not_useful"

def check_hallucination(state: AgentState):
    is_grounded = state.get("is_grounded") == "yes"
    retry_count = state.get("retry_count", 0)

    if is_grounded:
        logger.info("event=hallucination_gate outcome=grounded retry_count=%s", retry_count)
        return "grounded"
    
    # If it's a hallucination ('no') and we have retries left
    if not is_grounded and retry_count < 3:
        logger.warning("event=hallucination_gate outcome=hallucinated retry_count=%s", retry_count)
        return "hallucinated"
    
    # Final fallback: out of retries, just give the answer
    logger.warning("event=hallucination_gate outcome=grounded retry_count=%s fallback=max_retries", retry_count)
    return "grounded"

def answer_evaluator(state: AgentState):
    is_useful = state.get("is_useful") == "yes"
    retry_count = state.get("retry_count", 0)

    if is_useful:
        logger.info("event=answer_evaluator outcome=useful retry_count=%s", retry_count)
        return "useful"
    
    # If it's a hallucination ('no') and we have retries left
    if not is_useful and retry_count < 3:
        logger.warning("event=answer_evaluator outcome=not_useful retry_count=%s", retry_count)
        return "not_useful"
    
    # Final fallback: out of retries, just give the answer
    logger.warning("event=answer_evaluator outcome=useful retry_count=%s fallback=max_retries", retry_count)
    return "useful"
