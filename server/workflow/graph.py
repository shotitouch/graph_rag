from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes import (
    analyze_query_node,
    answer_grader_node,
    generate_node,
    grade_documents_node,
    hallucination_grader_node,
    prepare_computation_context_node,
    prepare_retrieval_heavy_context_node,
    prepare_token_heavy_context_node,
    retrieve_node,
    retrieve_computation_heavy_node,
    retrieve_focused_lookup_node,
    retrieve_retrieval_heavy_node,
    retrieve_token_heavy_node,
    rewrite_node,
    router_node,
)
from .edges import (
    answer_evaluator,
    check_hallucination,
    route_after_doc_grading,
    route_based_on_intent,
    route_technical_coverage,
)

workflow = StateGraph(AgentState)

# Define Nodes
workflow.add_node("route_intent", router_node)
workflow.add_node("analyze_query", analyze_query_node)
workflow.add_node("retrieve_default", retrieve_node)
workflow.add_node("retrieve_focused_lookup", retrieve_focused_lookup_node)
workflow.add_node("retrieve_retrieval_heavy", retrieve_retrieval_heavy_node)
workflow.add_node("retrieve_token_heavy", retrieve_token_heavy_node)
workflow.add_node("retrieve_computation_heavy", retrieve_computation_heavy_node)
workflow.add_node("grade_docs", grade_documents_node)
workflow.add_node("prepare_retrieval_heavy_context", prepare_retrieval_heavy_context_node)
workflow.add_node("prepare_token_heavy_context", prepare_token_heavy_context_node)
workflow.add_node("prepare_computation_context", prepare_computation_context_node)
workflow.add_node("generate", generate_node)
workflow.add_node("rewrite", rewrite_node)
workflow.add_node("grade_hallucination", hallucination_grader_node)
workflow.add_node('grade_answer', answer_grader_node)

# Build Graph logic

workflow.add_edge(START, "route_intent")
workflow.add_conditional_edges(
    "route_intent", 
    route_based_on_intent, 
    {"conversational": "generate", "technical": "analyze_query"}
)
workflow.add_conditional_edges(
    "analyze_query",
    route_technical_coverage,
    {
        "default_technical": "retrieve_default",
        "focused_lookup": "retrieve_focused_lookup",
        "retrieval_heavy": "retrieve_retrieval_heavy",
        "token_heavy": "retrieve_token_heavy",
        "computation_heavy": "retrieve_computation_heavy",
    }
)
workflow.add_edge("retrieve_default", "grade_docs")
workflow.add_edge("retrieve_focused_lookup", "grade_docs")
workflow.add_edge("retrieve_retrieval_heavy", "grade_docs")
workflow.add_edge("retrieve_token_heavy", "grade_docs")
workflow.add_edge("retrieve_computation_heavy", "grade_docs")
workflow.add_conditional_edges(
    "grade_docs",
    route_after_doc_grading,
    {
        "generate": "generate",
        "rewrite": "rewrite",
        "prepare_retrieval_heavy_context": "prepare_retrieval_heavy_context",
        "prepare_token_heavy_context": "prepare_token_heavy_context",
        "prepare_computation_context": "prepare_computation_context",
    }
)
workflow.add_edge("prepare_retrieval_heavy_context", "generate")
workflow.add_edge("prepare_token_heavy_context", "generate")
workflow.add_edge("prepare_computation_context", "generate")
workflow.add_edge("rewrite", "analyze_query")
workflow.add_conditional_edges(
    "generate",
    route_based_on_intent,
    {
        "conversational": END, 
        "technical": "grade_hallucination"
    }
)
workflow.add_conditional_edges(
    "grade_hallucination", 
    check_hallucination, 
    {"hallucinated": "rewrite", "grounded": 'grade_answer'}
)
workflow.add_conditional_edges(
    "grade_answer", 
    answer_evaluator, 
    {"not_useful": "rewrite", "useful": END}
)


memory = MemorySaver()

agent_app = workflow.compile(checkpointer=memory)
