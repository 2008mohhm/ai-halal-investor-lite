"""Application factory for the educational investor dashboard."""

from flask import Flask, render_template

from .db import initialize_database
from .watchlist import WatchlistError, load_watchlist


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="development-only-change-me",
        DATABASE_PATH=f"{app.instance_path}/investor.sqlite3",
        WATCHLIST_PATH="config/watchlist.json",
    )
    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])

    @app.get("/")
    def index():
        try:
            watchlist = load_watchlist(app.config["WATCHLIST_PATH"])
            error = None
        except WatchlistError as exc:
            watchlist, error = [], str(exc)
        return render_template("index.html", watchlist=watchlist, error=error)

    @app.get("/health")
    def health():
        return {"status": "ok", "trading_enabled": False}, 200

    return app
