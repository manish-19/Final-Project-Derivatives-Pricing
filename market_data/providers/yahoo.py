"""Yahoo Finance market-data provider (Phase 1 primary source)."""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import yfinance as yf

from market_data.providers.base import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Retrieve US equity option chains via Yahoo Finance (yfinance)."""

    name = "yahoo"

    def get_spot_price(self, symbol: str) -> float:
        ticker = yf.Ticker(symbol.upper())
        # Prefer fast_info; fall back to info fields used on the Yahoo quote page.
        try:
            price = float(ticker.fast_info["lastPrice"])
            if price > 0:
                return price
        except Exception:
            pass

        info = ticker.info
        for key in ("currentPrice", "regularMarketPrice", "previousClose"):
            value = info.get(key)
            if value is not None and float(value) > 0:
                return float(value)

        raise RuntimeError(f"Could not retrieve underlying price for {symbol.upper()}")

    def get_expirations(self, symbol: str) -> list[date]:
        ticker = yf.Ticker(symbol.upper())
        raw = ticker.options
        if not raw:
            raise RuntimeError(f"No option expirations found for {symbol.upper()}")
        return [datetime.strptime(item, "%Y-%m-%d").date() for item in raw]

    def get_option_chain(self, symbol: str, expiry: date) -> tuple[pd.DataFrame, pd.DataFrame]:
        ticker = yf.Ticker(symbol.upper())
        expiry_str = expiry.isoformat()
        try:
            chain = ticker.option_chain(expiry_str)
        except Exception as exc:  # yfinance raises varying errors by version
            raise RuntimeError(
                f"Could not fetch Yahoo option chain for {symbol.upper()} {expiry_str}: {exc}"
            ) from exc

        calls = _normalise_chain_frame(chain.calls)
        puts = _normalise_chain_frame(chain.puts)
        return calls, puts

    def get_dividend_yield(self, symbol: str) -> float | None:
        """Return annual yield as a decimal for later use as q.

        Yahoo's `info['dividendYield']` is often a percent-style number
        (e.g. 0.33 meaning about 0.33%), while
        `trailingAnnualDividendYield` is usually already a decimal
        (e.g. 0.0033). We prefer the trailing field when present.
        """
        info = yf.Ticker(symbol.upper()).info
        trailing = info.get("trailingAnnualDividendYield")
        if trailing is not None and float(trailing) >= 0:
            return float(trailing)

        raw = info.get("dividendYield")
        if raw is None:
            return None

        value = float(raw)
        # Heuristic: values like 0.33 for AAPL are percent points, not 33%.
        if value > 0.05:
            return value / 100.0
        return value


def _normalise_chain_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "strike",
                "bid",
                "ask",
                "lastPrice",
                "volume",
                "openInterest",
                "impliedVolatility",
            ]
        )

    out = df.copy()
    required = [
        "strike",
        "bid",
        "ask",
        "lastPrice",
        "volume",
        "openInterest",
        "impliedVolatility",
    ]
    for col in required:
        if col not in out.columns:
            out[col] = pd.NA
    return out[required].sort_values("strike").reset_index(drop=True)
