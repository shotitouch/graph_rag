# graph/nodes.py
from typing import Any, Dict
import asyncio
from core.retriever import get_reranked_docs
from core.chain import get_chain, get_rewrite_chain, get_grader_chain, get_hallucination_chain, get_answer_grader_chain, get_router_chain
from .state import AgentState
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from core.llm import llm
from utils.logger import get_logger

logger = get_logger(__name__)

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

async def router_node(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    logger.info("event=node_started node=route_intent")
    
    router_chain = get_router_chain()
    res = await router_chain.ainvoke({"question": question})
    # Using the robust extraction logic
    if isinstance(res, dict):
        decision = res.get("datasource", "technical")
    else:
        decision = getattr(res, "datasource", "technical")
    
    if decision not in ["conversational", "technical"]:
        decision = "technical"
        
    logger.info("event=node_completed node=route_intent intent=%s", decision)
    return {"intent": decision}

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
    logger.info("event=node_started node=grade_docs docs_count=%s", len(documents))
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
        logger.info("event=node_completed node=grade_docs docs_in=%s relevant_docs=%s", len(documents), len(relevant_docs))
        return {"documents": relevant_docs}
    
    except Exception as e:
        logger.exception("event=node_failed node=grade_docs")
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        raise e

async def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 1: Retrieve and Rerank documents.
    Uses the logic from retriever.py.
    """
    question = state["question"]
    messages = state.get("messages", [])
    logger.info("event=node_started node=retrieve")

    updates = {}

    if not messages or messages[-1].type == "ai":
        updates["messages"] = [HumanMessage(content=question)]
    
    # Use your existing reranking logic
    documents = await get_reranked_docs(question)
    updates["documents"] = documents
    logger.info("event=node_completed node=retrieve docs_count=%s", len(documents))

    return updates

async def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 2: Generate an answer using the retrieved context.
    Uses the logic from chain.py and prompt.py.
    """
    logger.info("event=node_started node=generate")

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

        return {
            "messages": [AIMessage(content=generation)], 
            "generation": generation,
            "sources": sources,
        }
    except Exception as e:
        logger.exception("event=node_failed node=generate")
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        raise e


async def rewrite_node(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    history = state.get("messages", [])
    current_retry = state.get("retry_count", 0)
    is_grounded = state.get("is_grounded")
    is_useful = state.get("is_useful")
    documents = state.get("documents", [])

    reason = "The initial search didn't find relevant documents."
    if documents and is_grounded == "no":
        reason = "The previous answer was a hallucination; it wasn't supported by the facts found."
    elif documents and is_useful == "no":
        reason = "The previous answer didn't sufficiently answer the user's specific question."
    logger.warning("event=node_started node=rewrite retry_count=%s reason=%s", current_retry, reason)

    # 1. The Rewrite Logic
    rewriter = get_rewrite_chain()
    better_question = await rewriter.ainvoke({
        "history": history,
        "question": question,
        "reason": reason
    })

    logger.info("event=node_completed node=rewrite retry_count=%s", current_retry + 1)

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
    logger.info("event=node_started node=grade_hallucination docs_count=%s", len(documents))

    if not documents:
        logger.warning("event=node_completed node=grade_hallucination outcome=skipped_no_documents")
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


    logger.info("event=node_completed node=grade_hallucination grounded=%s", score.lower())
    return {"is_grounded": score.lower()}

async def answer_grader_node(state: AgentState) -> Dict[str, Any]:
    generation = state["generation"]
    question = state["question"]
    logger.info("event=node_started node=grade_answer")

    if not generation or not question:
        logger.warning("event=node_completed node=grade_answer outcome=missing_generation")
        return {"is_useful": "no", "documents": []}
    
    try:
        # 1. Run the Answer Grader Chain
        # Note: You'll need get_answer_grader_chain in core/chain.py
        grader_chain = get_answer_grader_chain()
        res = await grader_chain.ainvoke({
            "question": question, 
            "generation": generation
        })

        score = get_binary_score(res)

        logger.info("event=node_completed node=grade_answer useful=%s", score)
        return {
            "is_useful": score,
            "documents": [] # memory cleanup
        }

    except Exception as e:
        logger.exception("event=node_failed node=grade_answer")
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        return {"is_useful": "no", "documents": []}
