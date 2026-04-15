from core.prompt import prompt, re_write_prompt, grader_prompt, hallucination_prompt, answer_grader_prompt, query_analysis_prompt, router_prompt
from core.llm import llm
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import Literal, Optional

parser = StrOutputParser()

class RouteQuery(BaseModel):
    """Route a user query to the most appropriate node."""
    datasource: Literal["conversational", "technical"] = Field(
        description="Given a user question choose to route it to 'conversational' or 'technical'.",
    )

def get_router_chain():
    return router_prompt | llm.with_structured_output(RouteQuery)

class AnalyzeTenQQuery(BaseModel):
    """Structured analysis of a 10-Q technical question."""

    question_type: Literal[
        "fact_lookup",
        "metric_lookup",
        "performance_summary",
        "risk_or_disclosure",
        "general_technical",
    ] = Field(description="The best-fit 10-Q question category.")
    scope_type: Literal[
        "current_filing",
        "single_company",
        "multi_company_comparison",
        "market_wide",
        "aggregate",
        "unknown",
    ] = Field(description="The scope implied by the question.")
    query_tickers: list[str] = Field(
        default_factory=list,
        description="Relevant uppercase ticker symbols explicitly mentioned or safely implied by the question.",
    )
    query_year: Optional[int] = Field(
        default=None,
        description="Explicit year requested by the user, if any.",
    )
    query_period: Optional[Literal["Q1", "Q2", "Q3"]] = Field(
        default=None,
        description="Explicit quarter requested by the user, if any.",
    )
    multi_question: bool = Field(
        default=False,
        description="Whether the user asked multiple distinct filing questions in one message.",
    )
    focus_terms: list[str] = Field(
        default_factory=list,
        description="Short list of retrieval-oriented financial terms.",
    )

def get_query_analysis_chain():
    return query_analysis_prompt | llm.with_structured_output(AnalyzeTenQQuery)

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
