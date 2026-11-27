"""SQLite storage for daily OHLCV bars."""

import sqlite3
from pathlib import Path


def initialize_database(database_path):
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("INSERT OR IGNORE INTO app_meta (key, value) VALUES (?, ?)", ("schema_version", "2"))
        connection.execute(
            "CREATE TABLE IF NOT EXISTS daily_bars ("
            "symbol TEXT NOT NULL, date TEXT NOT NULL, open REAL NOT NULL, high REAL NOT NULL, "
            "low REAL NOT NULL, close REAL NOT NULL, volume REAL NOT NULL, "
            "PRIMARY KEY(symbol, date))"
        )


def store_bars(database_path, symbol, bars):
    with sqlite3.connect(database_path) as connection:
        connection.executemany(
            "INSERT INTO daily_bars(symbol,date,open,high,low,close,volume) VALUES(?,?,?,?,?,?,?) "
            "ON CONFLICT(symbol,date) DO UPDATE SET open=excluded.open, high=excluded.high, "
            "low=excluded.low, close=excluded.close, volume=excluded.volume",
            [(symbol, b.date, b.open, b.high, b.low, b.close, b.volume) for b in bars],
        )


def load_bars(database_path, symbol, limit=500):
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT date,open,high,low,close,volume FROM daily_bars WHERE symbol=? ORDER BY date DESC LIMIT ?",
            (symbol, limit),
        ).fetchall()
    from .analysis import Bar
    return [Bar(*row) for row in reversed(rows)]
