from investor import create_app


def test_dashboard_and_health_are_non_trading(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(tmp_path / "test.sqlite3"),
            "WATCHLIST_PATH": "config/watchlist.json",
        }
    )
    client = app.test_client()
    page = client.get("/")
    assert page.status_code == 200
    assert "AAPL" in page.get_data(as_text=True)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json["trading_enabled"] is False
