import json

from investor.watchlist import WatchlistError, is_allowed, load_watchlist


def test_initial_user_supplied_symbols_are_loaded():
    rows = load_watchlist("config/watchlist.json")
    assert [row["symbol"] for row in rows] == [
        "AAPL", "NVDA", "MSFT", "GOOGL", "AVGO", "TSLA", "LLY", "MU", "AMD",
        "XOM", "JNJ", "CSCO", "PG", "AMAT", "LRCX", "PANW", "TXN", "LIN",
    ]
    assert len(rows) == 18


def test_allowlist_is_exact_and_rejects_unknown_symbols():
    assert is_allowed("GOOGL", "config/watchlist.json")
    assert not is_allowed("googl", "config/watchlist.json")
    assert not is_allowed("NOPE", "config/watchlist.json")
    assert not is_allowed("AAPL;DROP", "config/watchlist.json")


def test_malformed_or_duplicate_config_fails_closed(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"symbols": [{"symbol": "AAPL"}, {"symbol": "AAPL"}]}))
    try:
        load_watchlist(bad)
    except WatchlistError:
        pass
    else:
        raise AssertionError("duplicate symbols should be rejected")
    assert not is_allowed("AAPL", bad)
