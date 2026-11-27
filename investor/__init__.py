"""Application factory for the educational dashboard and local reports."""

import json
from flask import Flask, Response, jsonify, render_template

from .analysis import strategy_signals
from .backtest import simple_backtest
from .db import initialize_database, load_bars
from .reports import report_for_symbol, arabic_summary
from .risk import emergency_stop_enabled, validate_risk_request
from .watchlist import WatchlistError, is_allowed, load_watchlist


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="development-only-change-me",
        DATABASE_PATH=f"{app.instance_path}/investor.sqlite3",
        WATCHLIST_PATH="config/watchlist.json",
        FUNDAMENTALS_PATH="config/fundamentals.json",
        KILL_FILE="KILL",
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
                item["report"] = report_for_symbol(item["symbol"], bars)
                item["last_close"] = bars[-1].close if bars else None
                item["last_date"] = bars[-1].date if bars else None
            error = None
        except WatchlistError as exc:
            watchlist, error = [], str(exc)
        return render_template("index.html", watchlist=watchlist, error=error,
                               stopped=emergency_stop_enabled(app.config["KILL_FILE"]))

    @app.post("/api/risk-check")
    def risk_check():
        body = app.ensure_sync(request_json)
        result = validate_risk_request(body.get("cash"), body.get("quantity"), body.get("price"))
        return jsonify(result), 200

    @app.get("/api/analysis/<symbol>")
    def analysis_api(symbol):
        if not is_allowed(symbol, app.config["WATCHLIST_PATH"]):
            return {"error": "الرمز غير موجود في القائمة البيضاء"}, 404
        bars = load_bars(app.config["DATABASE_PATH"], symbol)
        return strategy_signals(bars), 200

    @app.get("/api/backtest/<symbol>")
    def backtest_api(symbol):
        if not is_allowed(symbol, app.config["WATCHLIST_PATH"]):
            return {"error": "الرمز غير موجود في القائمة البيضاء"}, 404
        bars = load_bars(app.config["DATABASE_PATH"], symbol)
        result = simple_backtest(bars)
        return jsonify(result), 200

    @app.get("/api/report/<symbol>/<period>")
    def report_api(symbol, period):
        if not is_allowed(symbol, app.config["WATCHLIST_PATH"]):
            return {"error": "الرمز غير موجود في القائمة البيضاء"}, 404
        if period not allowed_report_period:
            return {"error": "فترة التقرير غير مدعومة"}, 400
        bars = load_bars(app.config["DATABASE_PATH"], symbol)
        limits = {"daily": 1, "weekly": 7, "monthly": 30}
        report = report_for_symbol(symbol, bars[-limits[period]:])
        return jsonify({"period": period, "summary": arabic_summary(report), "report": report}), 200

    @app.post("/api/kill")
    def create_kill():
        Path(app.config["KILL_FILE"]).touch()
        return jsonify({"stopped": True}), 200

    @app.post("/api/unkill")
    def remove_kill():
        Path(app.config["KILL_FILE"]).unlink(missing_ok=True)
        return jsonify({"stopped": False}), 200

    @app.get("/health")
    def health():
        return {"status": "ok", "trading_enabled": False,
                "stopped": emergency_stop_enabled(app.config["KILL_FILE"])}, 200

    return app
