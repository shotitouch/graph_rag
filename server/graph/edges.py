from .state import AgentState

def route_based_on_intent(state: AgentState):
    """
    Looks at the intent stored in state and decides 
    whether to go to the RAG path or the Chat path.
    """
    print("---DECIDING NEXT STEP BASED ON INTENT---")
    
    intent = state.get("intent")
    
    if intent == "conversational":
        print("---ROUTE: DIRECT TO CONVERSATIONAL PATH---")
        return "conversational"
    
    # Default to technical if something goes wrong or it's classified as such
    print("---ROUTE: TO TECHNICAL- PATH--")
    return "technical"

def route_after_generate(state: AgentState):
    print("---DECIDING NEXT STEP BASED ON INTENT---")
    
    intent = state.get("intent")
    
    if intent == "conversational":
        print("---ROUTE: DIRECT TO END---")
        return "conversational"
    
    # Default to technical if something goes wrong or it's classified as such
    print("---ROUTE: TO RETRIEVE (TECHNICAL)---")
    return "technical"

def doc_grader(state: AgentState):
    """
    Determines whether to generate an answer, rewrite the query, or exit.
    """
    print("---ASSESSING GRADED DOCUMENTS---")
    
    documents = state.get("documents", [])
    retry_count = state.get("retry_count", 0)

    # 1. If we found documents, move to generation
    if documents:
        print("---DECISION: USEFUL (Proceeding to Generate)---")
        return "useful"

    # 2. Safety Break: If no docs found, check if we've exhausted retries
    if retry_count >= 3:
        print(f"---DECISION: NOT USEFUL (Max retries {retry_count} reached)---")
        # You can route to "generate" anyway to have the LLM say "I don't know"
        # or route to a specific 'failure' node.
        return "useful" 

    # 3. If no docs and we still have retries left, rewrite
    print(f"---DECISION: NOT USEFUL (Retry {retry_count}/3)---")
    return "not_useful"

def check_hallucination(state: AgentState):
    is_grounded = state.get("is_grounded") == "yes"
    retry_count = state.get("retry_count", 0)

    if is_grounded:
        print("---DECISION: GROUNDED (Proceeding to Answer Evaluator)---")
        return "grounded"
    
    # If it's a hallucination ('no') and we have retries left
    if not is_grounded and retry_count < 3:
        print(f"---DECISION: HALLUCINATION (Retry {retry_count+1}/3)---")
        return "hallucinated"
    
    # Final fallback: out of retries, just give the answer
    print("---DECISION: MAX RETRIES REACHED (Passing anyway)---")
    return "grounded"

def answer_evaluator(state: AgentState):
    print('---EVALUATING ANSWER---')
    
    is_useful = state.get("is_useful") == "yes"
    retry_count = state.get("retry_count", 0)

    if is_useful:
        print("---DECISION: USEFUL (Proceeding to END)---")
        return "useful"
    
    # If it's a hallucination ('no') and we have retries left
    if not is_useful and retry_count < 3:
        print(f"---DECISION: NOT_USEFUL (Retry {retry_count+1}/3)---")
        return "not_useful"
    
    # Final fallback: out of retries, just give the answer
    print("---DECISION: MAX RETRIES REACHED (Passing anyway)---")
    return "useful"