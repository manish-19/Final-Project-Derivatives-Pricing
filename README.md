# Phase 1 — Market Data Collection (reference implementation)

Runnable reference for the instructor. Students type this live in `BSM/` while
reading the Video 1 spiekbrief. Do not copy wholesale into the recording folder
ahead of time.

## What this phase does

- CLI prompts: ticker → expiry → call/put → strike → manual `r`
- Fetches real US equity option data from **Yahoo Finance** (`yfinance`)
- Displays fields that should match the Yahoo option chain page
- Validates quote quality (crossed book, missing IV, wide spreads, …)
- **No Black-Scholes / no pricing**

## Provider design

```
cli.py  →  get_provider("yahoo")  →  YahooFinanceProvider
                ↑
         providers/__init__.py registry
```

Add Polygon/CBOE/NASDAQ/OptionMetrics later by:

1. Implementing `MarketDataProvider` in `providers/<name>.py`
2. Registering it in `providers/__init__.py`
3. Leaving `cli.py` unchanged (aside from optional `--provider` choices)

## Run

```bash
cd reference/phase1-market-data
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python cli.py
```

## Verify against Yahoo

Open the same symbol / expiry / strike on finance.yahoo.com options and compare
bid, ask, last, volume, open interest, and implied volatility.

Notes:

- Yahoo `dividendYield` is messy; we prefer `trailingAnnualDividendYield` as decimal `q`.
- Deep ITM/OTM implied vols on Yahoo are often noisy — validation will warn.
- Risk-free rate is **manual** in Phase 1 on purpose.
