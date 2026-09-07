from data.market_data import YahooMarketDataCollector
from services.pricing_service import PricingService
from infra.cache.cache import build_cache

def run(ticker="AAPL", dte=30):
    cache = build_cache()
    market = YahooMarketDataCollector(ticker=ticker)
    service = PricingService(market, cache)
    return service.price_atm(dte=dte)
