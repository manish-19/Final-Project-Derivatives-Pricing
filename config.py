import os

APP_NAME = os.getenv("APP_NAME", "derivatives-pricing")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "30"))
IV_CACHE_TTL_SECONDS = int(os.getenv("IV_CACHE_TTL_SECONDS", "60"))
MARKET_CACHE_TTL_SECONDS = int(os.getenv("MARKET_CACHE_TTL_SECONDS", "5"))
CACHE_NAMESPACE = os.getenv("CACHE_NAMESPACE", "deriv:v1")
REDIS_URL = os.getenv("REDIS_URL", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
STALE_AFTER_SECONDS = int(os.getenv("STALE_AFTER_SECONDS", "10"))
