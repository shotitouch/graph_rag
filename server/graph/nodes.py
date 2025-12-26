# graph/nodes.py
from typing import Any, Dict
import asyncio
from core.retriever import get_reranked_docs
from core.chain import get_chain, get_rewrite_chain, get_grader_chain, get_hallucination_chain, get_answer_grader_chain, get_router_chain
from .state import AgentState
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from core.llm import llm

async def router_node(state: AgentState) -> Dict[str, Any]:
    print("---ROUTING NODE---")
    question = state["question"]
    
    router_chain = get_router_chain()
    res = await router_chain.ainvoke({"question": question})
    print(res)
    # Using the robust extraction logic
    if isinstance(res, dict):
        decision = res.get("datasource", "technical")
    else:
        decision = getattr(res, "datasource", "technical")
    
    if decision not in ["conversational", "technical"]:
        decision = "technical"
        
    print(f"---INTENT CLASSIFIED AS: {decision}---")
    return {"intent": decision}

def get_binary_score(res) -> str:
    """Extracts binary_score safely from an LLM response."""
    if res is None:
        return "no"
    
    if isinstance(res, dict):
        return str(res.get("binary_score", "no")).lower()
    
    return str(getattr(res, "binary_score", "no")).lower()

async def grade_documents_node(state: AgentState) -> Dict[str, Any]:
    print("---CHECKING DOCUMENT RELEVANCE---")
    question = state["question"]
    documents = state["documents"]
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
        print(f"---FOUND {len(relevant_docs)} RELEVANT DOCUMENTS---")
        return {"documents": relevant_docs}
    
    except Exception as e:
        print(f"CRITICAL ERROR in grade_documents_node: {str(e)}")
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        raise e

async def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 1: Retrieve and Rerank documents.
    Uses the logic from retriever.py.
    """
    print("---RETRIEVING---")
    question = state["question"]
    messages = state.get("messages", [])

    updates = {}

    if not messages or messages[-1].type == "ai":
        updates["messages"] = [HumanMessage(content=question)]
    
    # Use your existing reranking logic
    documents = await get_reranked_docs(question)
    updates["documents"] = documents

    return updates

async def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 2: Generate an answer using the retrieved context.
    Uses the logic from chain.py and prompt.py.
    """
    print("---GENERATING---")

    try:
        question = state.get("question")
        documents = state.get("documents", [])
        full_history = state.get("messages", [])
        trimmed_history = trimmed_history = full_history[-6:] if full_history else [] # simple limit history len, reduce memory usage
        print(trimmed_history)
        # Format context for the prompt
        context_chunks = []
        for d in documents:
            file = d.metadata.get("file") or d.metadata.get("source")
            page = d.metadata.get("page")
            citation_tag = f"[Source: {file}, page: {page}]"
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
        }
    except Exception as e:
        print(f"CRITICAL ERROR in generate_node: {str(e)}")
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        raise e


async def rewrite_node(state: AgentState) -> Dict[str, Any]:
    print("---REWRITING QUERY---")
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

    # 1. The Rewrite Logic
    rewriter = get_rewrite_chain()
    better_question = await rewriter.ainvoke({
        "history": history,
        "question": question,
        "reason": reason
    })

    print(f"Original: {question}")
    print(f"Rewritten: {better_question}")
    print(f"Retry Count: {current_retry + 1}")

    # 2. Return the new question AND increment the retry count
    return {
        "question": better_question, 
        "retry_count": state.get("retry_count", 0) + 1,
        # THE CLEANING PART:
        "generation": "",      # Erase the old answer
        "is_grounded": "",     # Erase the old grade
        "is_useful": "",       # Erase the old grade
        "documents": []        # Clear old docs so we don't reuse them
    }



async def hallucination_grader_node(state: AgentState) -> Dict[str, Any]:
    print("---CHECKING FOR HALLUCINATIONS---")
    generation = state["generation"]
    documents = state["documents"]

    if not documents:
        print("---SKIP HALLUCINATION CHECK: NO DOCUMENTS---")
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


    print(f"---HALLUCINATION SCORE: {score}---")
    return {"is_grounded": score.lower()}

async def answer_grader_node(state: AgentState) -> Dict[str, Any]:
    print("---CHECKING ANSWER RELEVANCE/UTILITY---")
    generation = state["generation"]
    question = state["question"]

    if not generation or not question:
        print("---NO GENERATION FOUND TO GRADE---")
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

        print(f"---ANSWER UTILITY SCORE: {score}---")
        return {
            "is_useful": score,
            "documents": [] # memory cleanup
        }

    except Exception as e:
        print(f"CRITICAL ERROR in answer_grader_node: {str(e)}")
        # This will print the actual error (e.g., API Key missing, Rate Limit, etc.)
        return {"is_useful": "no", "documents": []}