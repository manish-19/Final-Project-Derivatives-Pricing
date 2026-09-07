# Architecture

## Direct conversion
Market data -> pricing models -> strategies -> analytics -> visualization/validation.

## Production-oriented extension

Market feed
   |
   v
Market Snapshot / In-Memory Hot Path
   |
   +----> Pricing Models (BSM / CRR / LR / Black-76 / MC / Barrier)
   |
   +----> Redis (shared/reference/derived cache)
   |          |
   |          +-- option-chain snapshots
   |          +-- IV surfaces
   |          +-- static/reference data
   |          +-- expensive derived analytics
   |
   +----> Durable storage adapter
   |
   v
Pricing / Analytics Service
   |
   v
Internal API / Research CLI

## What Redis is for

1. Cache option-chain/reference snapshots with very short TTLs.
2. Cache implied-volatility surfaces keyed by symbol + expiry + market snapshot version.
3. Cache expensive scenario grids/backtest metadata when inputs are immutable.
4. Share reference data between workers.
5. Provide a fast coordination layer where appropriate.

## What Redis is NOT for

Do not put every Black-Scholes/Monte-Carlo call through Redis. For latency-sensitive
pricing, serialize market state once, keep it in memory, and calculate locally. Redis adds
network/serialization overhead and should not become the critical per-request calculator.

## Cache key examples

deriv:v1:snapshot:AAPL
deriv:v1:chain:AAPL:2026-12-18:<snapshot_version>
deriv:v1:iv_surface:AAPL:2026-12-18:<snapshot_version>
deriv:v1:scenario:AAPL:<model>:<scenario_hash>

## Invalidation

Market snapshot changes -> publish/record a new snapshot version -> old derived keys naturally
expire or are explicitly invalidated. This prevents silently reusing calculations against a
different market state.

## Trading-firm considerations

- deterministic inputs and reproducibility
- monotonic timestamps / sequence numbers
- stale-data guards
- batch pricing
- vectorization
- warm workers
- structured logs and metrics
- circuit breakers/timeouts around external market-data providers
- no external Yahoo Finance dependency in the true trading hot path
- separate research/backtest workloads from latency-sensitive pricing
