"""Provider registry — CLI depends on names, not concrete classes."""

from __future__ import annotations

from market_data.providers.base import MarketDataProvider
from market_data.providers.yahoo import YahooFinanceProvider

# Future: from market_data.providers.polygon import PolygonProvider
# Future: from market_data.providers.cboe import CboeProvider

_PROVIDERS: dict[str, type[MarketDataProvider]] = {
    "yahoo": YahooFinanceProvider,
    # "polygon": PolygonProvider,
    # "cboe": CboeProvider,
    # "nasdaq": NasdaqProvider,
    # "optionmetrics": OptionMetricsProvider,
}


def available_providers() -> list[str]:
    return sorted(_PROVIDERS.keys())


def get_provider(name: str = "yahoo") -> MarketDataProvider:
    key = name.strip().lower()
    try:
        cls = _PROVIDERS[key]
    except KeyError as exc:
        known = ", ".join(available_providers())
        raise ValueError(f"Unknown provider {name!r}. Known: {known}") from exc
    return cls()
