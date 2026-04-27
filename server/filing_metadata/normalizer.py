from filing_metadata.schemas import TenQMetadata


def normalize_tenq_metadata(
    ticker: str | None,
    year: int | None,
    period: str | None,
) -> TenQMetadata:
    normalized_ticker = ticker.strip().upper() if isinstance(ticker, str) and ticker.strip() else None
    normalized_year = year if isinstance(year, int) else None
    normalized_period = period if period in {"Q1", "Q2", "Q3"} else None

    return TenQMetadata(
        ticker=normalized_ticker,
        year=normalized_year,
        period=normalized_period,
    )
