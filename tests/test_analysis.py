import json

from investor.analysis import Bar, atr, fundamental_filter, market_regime, rsi, sma, strategy_signals, validate_bars


def sample_bars(count=60):
    return [Bar(f"2025-01-{i + 1:02d}", 100+i, 101+i, 99+i, 100+i, 1000) for i in range(count)]


def test_indicators_are_pure_python_and_handle_short_series():
    closes = list(range(1, 61))
    assert sma(closes, 20) == 50.5
    assert rsi(closes) == 100
    assert atr(sample_bars()) == 2
    assert sma([1, 2], 20) is None
    assert market_regime(closes) == "UPTREND"


def test_anomalies_block_all_strategy_signals():
    bars = sample_bars()
    bars[-1] = Bar("2025-03-01", 200, 202, 199, 201, 1000)
    result = strategy_signals(bars, {"data_verified": True, "revenue_positive": True, "debt_to_equity": 0.1})
    assert result["anomalies"]
    assert all(value == "NO_SIGNAL" for value in result["signals"].values())


def test_fundamental_filter_fails_closed():
    assert fundamental_filter(None)["status"] == "UNKNOWN"
    assert fundamental_filter({"data_verified": True, "revenue_positive": True, "debt_to_equity": 0.31})["status"] == "FAIL"
    assert fundamental_filter({"data_verified": True, "revenue_positive": True, "debt_to_equity": 0.1})["status"] == "PASS"


def test_csv_parser_and_invalid_data():
    from investor.market_data import MarketDataError, parse_stooq_csv
    text = "Date,Open,High,Low,Close,Volume\n2025-01-02,10,11,9,10.5,100\n2025-01-01,9,10,8,9.5,90\n"
    parsed = parse_stooq_csv(text, "AAPL")
    assert [b.date for b in parsed] == ["2025-01-01", "2025-01-02"]
    try:
        parse_stooq_csv("Nope\nabc\n", "AAPL")
    except MarketDataError:
        pass
    else:
        raise AssertionError("invalid schema should fail")


def test_market_data_refuses_unlisted_symbol():
    from investor.market_data import MarketDataError, fetch_daily_bars
    try:
        fetch_daily_bars("NOPE", "config/watchlist.json")
    except MarketDataError:
        pass
    else:
        raise AssertionError("unlisted symbol should fail before networking")


def test_database_and_analysis_api_stay_read_only(tmp_path):
    from investor import create_app
    app = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db"), "WATCHLIST_PATH": "config/watchlist.json"})
    client = app.test_client()
    response = client.get("/api/analysis/NOPE")
    assert response.status_code == 404
    assert client.get("/api/analysis/AAPL").json["regime"] == "INSUFFICIENT_DATA"
    assert client.get("/health").json["trading_enabled"] is False
