from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import retrieve_node, generate_node, rewrite_node, grade_documents_node, hallucination_grader_node, answer_grader_node, router_node
from .edges import doc_grader, answer_evaluator, check_hallucination, route_based_on_intent

workflow = StateGraph(AgentState)

# Define Nodes
workflow.add_node("route_intent", router_node)
workflow.add_node("retrieve", retrieve_node)   # Uses retriever.py
workflow.add_node("grade_docs", grade_documents_node)
workflow.add_node("generate", generate_node)   # Uses chain.py
workflow.add_node("rewrite", rewrite_node)     # New node to refine query
workflow.add_node("grade_hallucination", hallucination_grader_node)
workflow.add_node('grade_answer', answer_grader_node)

# Build Graph logic

workflow.add_edge(START, "route_intent")
workflow.add_conditional_edges(
    "route_intent", 
    route_based_on_intent, 
    {"conversational": "generate", "technical": "retrieve"}
)
workflow.add_edge("retrieve", "grade_docs")
workflow.add_conditional_edges(
    "grade_docs", 
    doc_grader, 
    {"useful": "generate", "not_useful": "rewrite"}
)
workflow.add_edge("rewrite", "retrieve")
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