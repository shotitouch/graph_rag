from core.prompt import prompt, re_write_prompt, grader_prompt, hallucination_prompt, answer_grader_prompt, router_prompt
from core.llm import llm
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import Literal

parser = StrOutputParser()

class RouteQuery(BaseModel):
    """Route a user query to the most appropriate node."""
    datasource: Literal["conversational", "technical"] = Field(
        description="Given a user question choose to route it to 'conversational' or 'technical'.",
    )

def get_router_chain():
    return router_prompt | llm.with_structured_output(RouteQuery)

def get_chain():
    return prompt | llm | parser

def get_rewrite_chain():
    return re_write_prompt | llm | parser

# 1. For the Retriever
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(
        description="Documents are relevant to the user question, 'yes' or 'no'"
    )

# 2. For the Hallucination Checker
class GradeHallucinations(BaseModel):
    """Binary score for hallucination check in generation."""
    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

# 3. For the Answer Evaluator
class GradeAnswer(BaseModel):
    """Binary score to check if answer is useful/complete."""
    binary_score: str = Field(
        description="Answer addresses the user question, 'yes' or 'no'"
    )

def get_grader_chain(): return grader_prompt | llm.with_structured_output(GradeDocuments)
def get_hallucination_chain(): return hallucination_prompt | llm.with_structured_output(GradeHallucinations)
def get_answer_grader_chain(): return answer_grader_prompt | llm.with_structured_output(GradeAnswer)