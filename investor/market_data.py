"""Optional Stooq daily CSV reader; network access is explicit via the CLI only."""

import csv
import io
import urllib.error
import urllib.request
from datetime import date

from .analysis import Bar
from .watchlist import is_allowed


class MarketDataError(ValueError):
    pass


def parse_stooq_csv(text, symbol):
    reader = csv.DictReader(io.StringIO(text))
    required = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise MarketDataError("Unexpected market-data CSV schema")
    bars = []
    for row in reader:
        try:
            parsed_date = date.fromisoformat(row["Date"])
            if parsed_date > date.today():
                raise ValueError("future date")
            bars.append(Bar(row["Date"], *(float(row[key]) for key in ("Open", "High", "Low", "Close", "Volume"))))
        except (ValueError, TypeError, KeyError) as exc:
            raise MarketDataError(f"Invalid row for {symbol}") from exc
    bars.sort(key=lambda bar: bar.date)
    if not bars:
        raise MarketDataError(f"No daily data returned for {symbol}")
    if len({bar.date for bar in bars}) != len(bars):
        raise MarketDataError(f"Duplicate daily rows for {symbol}")
    return bars


def fetch_daily_bars(symbol, watchlist_path, timeout=10):
    if not is_allowed(symbol, watchlist_path):
        raise MarketDataError("Symbol is not on the user allowlist")
    # Host is fixed; user-controlled symbol is validated against the local allowlist.
    url = f"https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d"
    request = urllib.request.Request(url, headers={"User-Agent": "AI-Halal-Investor-Lite/0.1 educational"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise MarketDataError(f"Market data provider returned HTTP {response.status}")
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise MarketDataError("Market data response exceeds size limit")
        return parse_stooq_csv(payload.decode("utf-8-sig"), symbol)
    except (urllib.error.URLError, TimeoutError, UnicodeDecodeError) as exc:
        raise MarketDataError(f"Could not fetch daily data for {symbol}") from exc
