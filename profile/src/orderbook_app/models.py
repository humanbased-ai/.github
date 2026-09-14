from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable

from pydantic import BaseModel, Field


class OrderBookLevel(BaseModel):
    price: Decimal = Field(gt=0, allow_inf_nan=False)
    size: Decimal = Field(ge=0, allow_inf_nan=False)


class OrderBookSnapshot(BaseModel):
    venue: str
    symbol: str
    ts: datetime
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)


class OrderBookUpdate(BaseModel):
    venue: str
    symbol: str
    ts: datetime
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)


def parse_levels(levels: Iterable[Iterable[str | float]]) -> list[OrderBookLevel]:
    parsed = []
    for row in levels:
        values = list(row)
        if len(values) < 2:
            raise ValueError("orderbook levels require price and size")
        parsed.append(OrderBookLevel(price=Decimal(str(values[0])), size=Decimal(str(values[1]))))
    return parsed
