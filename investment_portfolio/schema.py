"""Utilities for deserializing portfolio configuration"""
from dataclasses import dataclass
from typing import List

from marshmallow import Schema, fields, post_dump


@dataclass
class PriceHistoryParams:
    """Parameters used for yfinance price history"""

    period: str
    interval: str


class PriceHistorySchema(Schema):
    """Deserialize price history parameters"""

    period = fields.String(default="1mo")
    interval = fields.String(default="1d")

    @post_dump
    def _to_dataclass(self, data, **kwargs) -> PriceHistoryParams:
        return PriceHistoryParams(**data)


@dataclass
class PortfolioParams:
    """Describe the portfolio and how it should be assessed"""

    ticker_symbols: List[str]
    price_history: PriceHistoryParams


class PortfolioSchema(Schema):
    """Deserialize portfolio configuration"""

    ticker_symbols = fields.List(fields.String())
    price_history = fields.Nested(PriceHistorySchema())

    @post_dump
    def _to_dataclass(self, data, **kwargs) -> PortfolioParams:
        return PortfolioParams(**data)
