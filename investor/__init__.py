"""Application factory for the educational investor dashboard."""

from flask import Flask, render_template

from .analysis import strategy_signals
from .db import initialize_database, load_bars
from .watchlist import WatchlistError, is_allowed, load_watchlist


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="development-only-change-me",
        DATABASE_PATH=f"{app.instance_path}/investor.sqlite3",
        WATCHLIST_PATH="config/watchlist.json",
        FUNDAMENTALS_PATH="config/fundamentals.json",
    )
    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])

    @app.get("/")
    def index():
        try:
            watchlist = load_watchlist(app.config["WATCHLIST_PATH"])
            for item in watchlist:
                bars = load_bars(app.config["DATABASE_PATH"], item["symbol"])
                report = strategy_signals(bars)
                item["report"] = report
                item["last_close"] = bars[-1].close if bars else None
                item["last_date"] = bars[-1].date if bars else None
            error = None
        except WatchlistError as exc:
            watchlist, error = [], str(exc)
        return render_template("index.html", watchlist=watchlist, error=error)

    @app.get("/api/analysis/<symbol>")
    def analysis_api(symbol):
        if not is_allowed(symbol, app.config["WATCHLIST_PATH"]):
            return {"error": "الرمز غير موجود في القائمة البيضاء"}, 404
        bars = load_bars(app.config["DATABASE_PATH"], symbol)
        return strategy_signals(bars), 200

    @app.get("/health")
    def health():
        return {"status": "ok", "trading_enabled": False}, 200

    return app
