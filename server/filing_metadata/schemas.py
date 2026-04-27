from typing import Literal, Optional

from pydantic import BaseModel


class TenQMetadata(BaseModel):
    ticker: Optional[str]
    year: Optional[int]
    period: Optional[Literal["Q1", "Q2", "Q3"]]
