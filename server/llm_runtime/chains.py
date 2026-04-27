from typing import Literal, Optional

from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from llm_runtime.client import llm
from llm_runtime.prompts import (
    answer_grader_prompt,
    computation_extraction_prompt,
    context_compression_prompt,
    grader_prompt,
    hallucination_prompt,
    prompt,
    query_analysis_prompt,
    re_write_prompt,
    router_prompt,
)

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
    coverage_type: Literal[
        "default_technical",
        "focused_lookup",
        "retrieval_heavy",
        "token_heavy",
        "computation_heavy",
    ] = Field(
        description="The first-pass technical coverage path to use for a single-filing question.",
    )
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

def get_context_compression_chain():
    return context_compression_prompt | llm | parser

def get_rewrite_chain():
    return re_write_prompt | llm | parser

class ComputationFact(BaseModel):
    label: str = Field(description="Short label for the extracted fact.")
    value: float = Field(description="Numeric value exactly supported by the evidence.")
    unit: str = Field(
        default="",
        description="Unit or scale label such as %, million, billion, or USD.",
    )
    citation_id: str = Field(description="Source ID supporting this fact, such as S1.")

class ComputationExtraction(BaseModel):
    operation: Literal[
        "difference",
        "percentage_change",
        "percentage_of_total",
        "ratio",
        "sum",
        "unsupported",
    ] = Field(description="Deterministic computation to run from the extracted facts.")
    result_label: str = Field(
        default="Computed result",
        description="Label to use when presenting the computed output.",
    )
    result_unit: str = Field(
        default="",
        description="Expected output unit or scale such as %, million, or USD.",
    )
    facts: list[ComputationFact] = Field(
        default_factory=list,
        description="Facts in the exact order needed for the deterministic computation.",
    )

def get_computation_extraction_chain():
    return computation_extraction_prompt | llm.with_structured_output(ComputationExtraction)

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
