import unittest
from infra.cache.cache import MemoryCache, key

class CacheTests(unittest.TestCase):
    def test_round_trip(self):
        c = MemoryCache()
        c.set(key("x", "AAPL"), {"spot": 100}, 10)
        self.assertEqual(c.get(key("x", "AAPL"))["spot"], 100)

    def test_delete(self):
        c = MemoryCache()
        k = key("x", "AAPL")
        c.set(k, 1, 10)
        c.delete(k)
        self.assertIsNone(c.get(k))

if __name__ == "__main__":
    unittest.main()
