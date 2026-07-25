"""Provider interface. Yahoo is Phase 1; Polygon/CBOE/etc. plug in later."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd

from market_data.models import OptionContractQuote, OptionRight


class MarketDataProvider(ABC):
    """Abstract market-data provider for equity options."""

    name: str

    @abstractmethod
    def get_spot_price(self, symbol: str) -> float:
        """Last / regular-market underlying price."""

    @abstractmethod
    def get_expirations(self, symbol: str) -> list[date]:
        """Available option expiration dates, ascending."""

    @abstractmethod
    def get_option_chain(self, symbol: str, expiry: date) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return (calls, puts) DataFrames for one expiry.

        Minimum columns after normalisation:
        strike, bid, ask, lastPrice, volume, openInterest, impliedVolatility
        """

    @abstractmethod
    def get_dividend_yield(self, symbol: str) -> float | None:
        """Annual dividend yield as a decimal (0.005 = 0.5%), or None."""

    def get_option_quote(
        self,
        symbol: str,
        expiry: date,
        strike: float,
        right: OptionRight,
        risk_free_rate: float,
    ) -> OptionContractQuote:
        """Fetch one contract and return a normalised quote."""
        calls, puts = self.get_option_chain(symbol, expiry)
        chain = calls if right == "call" else puts

        if chain.empty:
            raise ValueError(f"No {right} contracts for {symbol} {expiry.isoformat()}")

        matches = chain[chain["strike"] == float(strike)]
        if matches.empty:
            available = sorted(chain["strike"].unique().tolist())
            raise ValueError(
                f"Strike {strike} not found for {symbol} {expiry.isoformat()} {right}. "
                f"Available strikes include: {_preview_strikes(available)}"
            )

        row = matches.iloc[0]
        spot = self.get_spot_price(symbol)
        div = self.get_dividend_yield(symbol)

        return OptionContractQuote(
            symbol=symbol.upper(),
            underlying_price=float(spot),
            strike=float(row["strike"]),
            expiry=expiry,
            right=right,
            bid=_f(row.get("bid")),
            ask=_f(row.get("ask")),
            last_price=_f(row.get("lastPrice")),
            volume=_int_or_none(row.get("volume")),
            open_interest=_int_or_none(row.get("openInterest")),
            implied_volatility=_iv_decimal(row.get("impliedVolatility")),
            dividend_yield=div,
            risk_free_rate=float(risk_free_rate),
            source=self.name,
        )


def _f(value: object) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    return float(value)


def _int_or_none(value: object) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return int(value)


def _iv_decimal(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return float(value)


def _preview_strikes(strikes: list[float], limit: int = 8) -> str:
    if len(strikes) <= limit:
        return ", ".join(str(s) for s in strikes)
    head = ", ".join(str(s) for s in strikes[: limit // 2])
    tail = ", ".join(str(s) for s in strikes[-limit // 2 :])
    return f"{head}, ..., {tail}"
