import argparse
from main import run

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ticker", default="AAPL")
    p.add_argument("--dte", type=int, default=30)
    p.add_argument("--test", action="store_true")
    args = p.parse_args()
    if args.test:
        import unittest
        unittest.main(module="validation.tests", exit=False)
    else:
        run(args.ticker, args.dte)
