from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class MarketInputs:
    underlying_price: float
    risk_free_rate: float
    dividend_yield: float
    valuation_date: date

@dataclass(frozen=True)
class OptionContract:
    ticker: str
    option_type: str
    strike: float
    expiry_date: date
    implied_volatility: float | None = None
