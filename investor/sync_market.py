"""Command-line market-data refresh. Never submits broker orders."""

import argparse
import json

from . import create_app
from .db import store_bars
from .market_data import MarketDataError, fetch_daily_bars
from .watchlist import load_watchlist


def main():
    parser = argparse.ArgumentParser(description="Fetch public daily bars for allowlisted symbols")
    parser.add_argument("--symbol", action="append", help="Allowlisted ticker; repeat to select multiple")
    args = parser.parse_args()
    app = create_app()
    watchlist_path = app.config["WATCHLIST_PATH"]
    selected = args.symbol or [item["symbol"] for item in load_watchlist(watchlist_path)]
    for symbol in selected:
        try:
            bars = fetch_daily_bars(symbol, watchlist_path)
            store_bars(app.config["DATABASE_PATH"], symbol, bars)
            print(json.dumps({"symbol": symbol, "rows_saved": len(bars), "status": "ok"}))
        except MarketDataError as exc:
            print(json.dumps({"symbol": symbol, "status": "error", "message": str(exc)}))


if __name__ == "__main__":
    main()
