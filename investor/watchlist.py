"""Strict read-only allowlist loader. This module never adds symbols."""

import json
import re
from pathlib import Path

_SYMBOL = re.compile(r"^[A-Z][A-Z0-9.]{0,9}$")


class WatchlistError(ValueError):
    """Raised when the allowlist is missing or malformed."""


def load_watchlist(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rows = data["symbols"]
        symbols = [row["symbol"] for row in rows]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise WatchlistError("تعذر تحميل القائمة البيضاء؛ أوقف التطبيق حتى إصلاح الإعداد.") from exc

    if not symbols or any(not isinstance(symbol, str) or not _SYMBOL.fullmatch(symbol) for symbol in symbols):
        raise WatchlistError("القائمة البيضاء غير صالحة.")
    if len(set(symbols)) != len(symbols):
        raise WatchlistError("القائمة البيضاء تحتوي رموزاً مكررة.")
    return rows


def is_allowed(symbol, path):
    """Return true only for an exact, case-sensitive allowlist match."""
    if not isinstance(symbol, str) or not _SYMBOL.fullmatch(symbol):
        return False
    try:
        allowed = {row["symbol"] for row in load_watchlist(path)}
    except WatchlistError:
        return False
    return symbol in allowed
