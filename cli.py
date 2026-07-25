"""Interactive CLI for Phase 1 market-data collection.

Usage (from this folder):
    python cli.py
    python cli.py --provider yahoo
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from market_data.display import format_quote_report
from market_data.models import OptionRight
from market_data.providers import available_providers, get_provider
from market_data.providers.base import MarketDataProvider
from market_data.validation import validate_quote


def prompt_text(message: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"{message}{suffix}: ").strip()
    if not raw and default is not None:
        return default
    return raw


def prompt_float(message: str, default: float | None = None) -> float:
    while True:
        raw = prompt_text(message, None if default is None else str(default))
        try:
            return float(raw)
        except ValueError:
            print("  Please enter a number.")


def prompt_choice(message: str, options: list[str]) -> str:
    print(message)
    for i, option in enumerate(options, start=1):
        print(f"  [{i}] {option}")
    while True:
        raw = input("Select number: ").strip()
        try:
            idx = int(raw)
        except ValueError:
            print("  Enter a valid number.")
            continue
        if 1 <= idx <= len(options):
            return options[idx - 1]
        print(f"  Choose between 1 and {len(options)}.")


def prompt_right() -> OptionRight:
    label = prompt_choice("Call or put?", ["call", "put"])
    return "call" if label == "call" else "put"


def select_expiry(provider: MarketDataProvider, symbol: str) -> date:
    expiries = provider.get_expirations(symbol)
    labels = [d.isoformat() for d in expiries]
    print(f"\nFound {len(labels)} expiration(s) for {symbol.upper()}.")
    chosen = prompt_choice("Select an expiration date:", labels)
    return date.fromisoformat(chosen)


def select_strike(provider: MarketDataProvider, symbol: str, expiry: date, right: OptionRight) -> float:
    calls, puts = provider.get_option_chain(symbol, expiry)
    chain = calls if right == "call" else puts
    strikes = sorted({float(s) for s in chain["strike"].tolist()})
    if not strikes:
        raise RuntimeError(f"No strikes available for {symbol} {expiry} {right}")

    spot = provider.get_spot_price(symbol)
    nearest = min(strikes, key=lambda k: abs(k - spot))
    print(f"\nUnderlying ~ {spot:.2f}. Nearest listed strike: {nearest}")
    print(f"{len(strikes)} strikes available (showing up to 30 around the spot).")

    # Show a window around spot so the menu stays usable.
    ordered = sorted(strikes, key=lambda k: abs(k - spot))
    window = sorted(ordered[:30])
    labels = [
        f"{s}  <-- nearest to spot" if s == nearest else str(s) for s in window
    ]
    chosen_label = prompt_choice("Select a strike:", labels)
    return float(chosen_label.split()[0])


def run_interactive(provider_name: str) -> int:
    print("Phase 1 — Market Data Collection")
    print("No pricing models in this phase. Collect, display, validate.\n")

    provider = get_provider(provider_name)
    print(f"Provider: {provider.name}")

    symbol = prompt_text("Ticker symbol", "AAPL").upper()
    if not symbol:
        print("Ticker is required.")
        return 1

    try:
        spot = provider.get_spot_price(symbol)
        print(f"Spot price for {symbol}: {spot:.4f}")
    except Exception as exc:
        print(f"Failed to fetch spot for {symbol}: {exc}")
        return 1

    try:
        expiry = select_expiry(provider, symbol)
        right = prompt_right()
        strike = select_strike(provider, symbol, expiry, right)
        risk_free = prompt_float("Risk-free rate r as decimal (placeholder)", 0.05)

        quote = provider.get_option_quote(
            symbol=symbol,
            expiry=expiry,
            strike=strike,
            right=right,
            risk_free_rate=risk_free,
        )
    except Exception as exc:
        print(f"\nData retrieval failed: {exc}")
        return 1

    result = validate_quote(quote)
    print(format_quote_report(quote, result))
    return 0 if result.ok else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect US equity option market data for later pricing phases."
    )
    parser.add_argument(
        "--provider",
        default="yahoo",
        choices=available_providers(),
        help="Market data provider (default: yahoo). Add new providers in the registry.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run_interactive(args.provider)
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
