# Derivatives Pricing Engine — clean conversion + production trading architecture

This repository is a direct structural conversion of the supplied derivatives-pricing prompt,
followed by a separate production-oriented architecture layer.

## 1. Direct conversion

The requested structure is:

derivatives_pricing/
├── config.py
├── run.py
├── main.py
├── models/
│   ├── base.py
│   ├── black_scholes.py
│   ├── binomial.py
│   ├── black_76.py
│   ├── monte_carlo.py
│   └── barrier.py
├── strategies/
│   └── strategies.py
├── data/
│   └── market_data.py
├── analytics/
│   ├── implied_vol.py
│   ├── scenario_shock.py
│   └── backtest.py
├── visualization/
│   └── plots.py
└── validation/
    └── tests.py

The supplied source is retained under `legacy/` so the conversion can be reconciled against
the original 3000+ line implementation.

## 2. Trading-firm production layer

The second layer is deliberately separate from the direct conversion. It adds the pieces that
matter when this becomes a low-latency pricing/analytics service:

- Redis cache for market/reference data and expensive derived results
- cache-aside reads with explicit TTLs
- versioned cache keys
- stale-data detection
- request-id / structured logging
- repository boundary for future PostgreSQL/Parquet/market-data storage
- pricing service boundary so API transport does not own quantitative logic
- batch-friendly cache interfaces
- invalidation hooks for changed market snapshots
- health/readiness checks
- configuration through environment variables

## Important distinction

Redis should NOT be placed around every pricing calculation blindly. For a trading system,
the hot path should normally consume an immutable market-data snapshot and calculate from
memory. Redis is most useful for shared/reference/derived data, not as a substitute for the
in-memory market-data path.

The architecture here is a practical research/service design, not a claim that it reproduces
Jane Street's proprietary infrastructure.
