"""Pretty-print quotes for visual checks against Yahoo Finance."""

from __future__ import annotations

from market_data.models import OptionContractQuote
from market_data.validation import ValidationResult


def format_quote_report(quote: OptionContractQuote, validation: ValidationResult) -> str:
    mid = quote.mid
    spread = quote.spread
    market_price = quote.market_price
    iv = quote.implied_volatility
    div = quote.dividend_yield

    lines = [
        "",
        "=" * 60,
        f" Market data  |  {quote.symbol}  {quote.right.upper()}  |  source: {quote.source}",
        "=" * 60,
        f"  Underlying price     : {_money(quote.underlying_price)}",
        f"  Strike price         : {_money(quote.strike)}",
        f"  Expiry date          : {quote.expiry.isoformat()}",
        f"  Risk-free rate (r)   : {_pct(quote.risk_free_rate)}  (manual / placeholder)",
        f"  Dividend yield (q)   : {_pct(div) if div is not None else 'n/a'}",
        f"  Implied volatility   : {_pct(iv) if iv is not None else 'n/a'}  (from {quote.source})",
        f"  Market option price  : {_money(market_price) if market_price is not None else 'n/a'}  (mid preferred)",
        f"  Bid price            : {_money(quote.bid)}",
        f"  Ask price            : {_money(quote.ask)}",
        f"  Bid-ask spread       : {_money(spread) if spread is not None else 'n/a'}",
        f"  Last price           : {_money(quote.last_price)}",
        f"  Trading volume       : {_int(quote.volume)}",
        f"  Open interest        : {_int(quote.open_interest)}",
        "-" * 60,
    ]

    if validation.errors:
        lines.append("  Validation ERRORS:")
        lines.extend(f"    - {msg}" for msg in validation.errors)
    if validation.warnings:
        lines.append("  Validation warnings:")
        lines.extend(f"    - {msg}" for msg in validation.warnings)
    if validation.ok and not validation.warnings:
        lines.append("  Validation: OK")
    elif validation.ok:
        lines.append("  Validation: OK with warnings")
    else:
        lines.append("  Validation: FAILED")

    lines.append("=" * 60)
    lines.append(
        "Compare these figures with the Yahoo Finance option chain page for the same contract."
    )
    lines.append("")
    return "\n".join(lines)


def _money(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.4f}"


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.4f}%  ({value:.6f} decimal)"


def _int(value: int | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:,}"
