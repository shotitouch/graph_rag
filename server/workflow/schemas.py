from typing import TypedDict


class QuestionAnalysis(TypedDict):
    question_type: str
    coverage_type: str
    scope_type: str
    query_tickers: list[str]
    query_year: int | None
    query_period: str
    multi_question: bool
    focus_terms: list[str]
