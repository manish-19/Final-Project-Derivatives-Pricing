"""Shared market-data models for Phase 1 (no pricing)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal


OptionRight = Literal["call", "put"]


@dataclass(frozen=True)
class OptionContractQuote:
    """One option quote normalised across providers."""

    symbol: str
    underlying_price: float
    strike: float
    expiry: date
    right: OptionRight
    bid: float
    ask: float
    last_price: float
    volume: int | None
    open_interest: int | None
    implied_volatility: float | None  # decimal, e.g. 0.25 = 25%
    dividend_yield: float | None  # decimal continuous/annual yield proxy
    risk_free_rate: float  # decimal; manual/placeholder in Phase 1
    source: str

    @property
    def mid(self) -> float | None:
        if self.bid is None or self.ask is None:
            return None
        if self.bid < 0 or self.ask < 0:
            return None
        return 0.5 * (self.bid + self.ask)

    @property
    def spread(self) -> float | None:
        if self.bid is None or self.ask is None:
            return None
        return self.ask - self.bid

    @property
    def market_price(self) -> float | None:
        """Prefer mid when the book is usable; otherwise last trade."""
        mid = self.mid
        if mid is not None and self.bid > 0 and self.ask >= self.bid:
            return mid
        if self.last_price is not None and self.last_price > 0:
            return self.last_price
        return mid
