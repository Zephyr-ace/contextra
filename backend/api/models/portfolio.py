from pydantic import BaseModel, Field
from typing import List, Optional


class Position(BaseModel):
    symbol: str
    name: str
    quantity: int
    average_cost: float = Field(description="Average cost per share")
    market_value: float
    pl_percent: float = Field(description="Profit/Loss percentage")
    currency: Optional[str] = None
    color: Optional[str] = None


class Portfolio(BaseModel):
    positions: List[Position]
