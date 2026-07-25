"""Lightweight validation for retrieved market quotes (no pricing)."""

from __future__ import annotations

from dataclasses import dataclass

from market_data.models import OptionContractQuote


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    warnings: tuple[str, ...]
    errors: tuple[str, ...]


def validate_quote(quote: OptionContractQuote) -> ValidationResult:
    """Check that a quote is usable as a later model input."""
    errors: list[str] = []
    warnings: list[str] = []

    if quote.underlying_price <= 0:
        errors.append("Underlying price must be positive.")
    if quote.strike <= 0:
        errors.append("Strike must be positive.")

    if quote.bid < 0 or quote.ask < 0:
        errors.append("Bid and ask cannot be negative.")
    if quote.ask < quote.bid:
        errors.append("Crossed market: ask is below bid.")
    if quote.bid == 0 and quote.ask == 0 and quote.last_price <= 0:
        errors.append("No usable market price (bid/ask/last all empty).")

    spread = quote.spread
    mid = quote.mid
    if spread is not None and mid is not None and mid > 0 and spread / mid > 0.5:
        warnings.append("Wide bid-ask spread (>50% of mid); quote may be stale or illiquid.")

    if quote.implied_volatility is None:
        warnings.append("Implied volatility missing from provider.")
    elif quote.implied_volatility <= 0:
        warnings.append("Implied volatility is non-positive.")
    elif quote.implied_volatility > 2.0:
        warnings.append(
            "Implied volatility looks extreme (>200%). "
            "Deep ITM/OTM Yahoo IVs are often unreliable."
        )

    if quote.dividend_yield is None:
        warnings.append("Dividend yield unavailable; you may enter q manually later.")
    elif quote.dividend_yield < 0:
        errors.append("Dividend yield cannot be negative.")

    if quote.volume is None or quote.volume == 0:
        warnings.append("Volume is zero or missing.")
    if quote.open_interest is None or quote.open_interest == 0:
        warnings.append("Open interest is zero or missing.")

    return ValidationResult(ok=not errors, warnings=tuple(warnings), errors=tuple(errors))
