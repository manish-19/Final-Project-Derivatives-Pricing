class MarketDataRepository:
    """Persistence boundary; replace with PostgreSQL/Parquet/market-data adapter in production."""
    def get_snapshot(self, symbol):
        raise NotImplementedError
    def save_snapshot(self, snapshot):
        raise NotImplementedError
