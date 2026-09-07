from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    spot: float
    timestamp: datetime

    @property
    def age_seconds(self):
        return (datetime.now(timezone.utc) - self.timestamp).total_seconds()

    def is_stale(self, max_age_seconds):
        return self.age_seconds > max_age_seconds
