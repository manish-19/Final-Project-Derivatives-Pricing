from config import MARKET_CACHE_TTL_SECONDS, STALE_AFTER_SECONDS
from infra.cache.cache import key
from infra.market_data.snapshot import MarketSnapshot

class PricingService:
    """Application boundary: transport/API code does not own pricing logic."""
    def __init__(self, market_data, cache):
        self.market_data = market_data
        self.cache = cache

    def get_snapshot(self):
        symbol = self.market_data.ticker
        cache_key = key("snapshot", symbol)
        cached = self.cache.get(cache_key)
        if cached:
            snapshot = MarketSnapshot(**cached)
            if not snapshot.is_stale(STALE_AFTER_SECONDS):
                return snapshot

        spot = self.market_data.get_underlying_price()
        snapshot = MarketSnapshot(
            symbol=symbol,
            spot=spot,
            timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )
        self.cache.set(cache_key, {
            "symbol": snapshot.symbol,
            "spot": snapshot.spot,
            "timestamp": snapshot.timestamp.isoformat(),
        }, MARKET_CACHE_TTL_SECONDS)
        return snapshot

    def price_atm(self, dte=30):
        # Quantitative model invocation belongs here after the direct model modules are populated.
        snapshot = self.get_snapshot()
        return {"ticker": snapshot.symbol, "spot": snapshot.spot, "dte": dte}
