import re

from filing_metadata.schemas import TenQMetadata
from llm_runtime.client import llm

TRADING_SYMBOL_RE = re.compile(
    r"\bTrading\s+Symbol(?:s)?\b\s*[:\-]?\s*([A-Z]{1,6})\b",
    re.IGNORECASE,
)

EXCHANGE_TICKER_RE = re.compile(
    r"\(\s*(NASDAQ|NYSE|AMEX|NYSEAMERICAN)\s*:\s*([A-Z]{1,6})\s*\)",
    re.IGNORECASE,
)

ENDED_DATE_RE = re.compile(
    r"\b(?:quarterly\s+period|quarter|three\s+months)\s+ended\s+"
    r"(March|June|September)\s+\d{1,2},\s+(20\d{2})\b",
    re.IGNORECASE,
)

MONTH_TO_Q = {
    "march": "Q1",
    "june": "Q2",
    "september": "Q3",
}


def regex_extract_tenq_metadata(cover_text: str) -> TenQMetadata:
    """
    Deterministic, cheap extraction.
    Returns TenQMetadata and allows missing fields when the regex cannot find them.
    """
    text = cover_text or ""

    ticker = None
    ticker_match = TRADING_SYMBOL_RE.search(text)
    if ticker_match:
        ticker = ticker_match.group(1).upper()
    else:
        exchange_match = EXCHANGE_TICKER_RE.search(text)
        if exchange_match:
            ticker = exchange_match.group(2).upper()

    year = None
    period = None
    ended_match = ENDED_DATE_RE.search(text)
    if ended_match:
        month = ended_match.group(1).lower()
        year = int(ended_match.group(2))
        period = MONTH_TO_Q.get(month)

    return TenQMetadata(
        ticker=ticker,
        year=year,
        period=period,
    )


async def llm_extract_tenq_metadata(cover_text: str) -> TenQMetadata:
    structured_llm = llm.with_structured_output(TenQMetadata)

    prompt = f"""
Extract ticker, year, and quarter from this SEC Form 10-Q cover text.
Return the quarter only as Q1, Q2, or Q3.
If the quarter is unclear or does not map cleanly to Q1, Q2, or Q3, return null for period.

TEXT:
{cover_text}
"""

    result = await structured_llm.ainvoke(prompt)

    if isinstance(result, TenQMetadata):
        return result

    if isinstance(result, dict):
        period = result.get("period")
        if period not in {"Q1", "Q2", "Q3", None}:
            result = {**result, "period": None}
        return TenQMetadata(**result)

    raise TypeError(f"Unexpected metadata output type: {type(result).__name__}")
