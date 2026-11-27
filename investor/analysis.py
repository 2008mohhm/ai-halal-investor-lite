"""Pure-Python daily-price analytics. No orders or investment advice."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Bar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


def validate_bars(bars, max_daily_move=0.20):
    """Return (clean_bars, anomaly_messages); any anomaly blocks strategy output."""
    clean, anomalies, previous_close = [], [], None
    for index, bar in enumerate(bars):
        values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
        if not all(isfinite(value) for value in values):
            anomalies.append(f"{bar.date}: non-finite value")
            continue
        if min(bar.open, bar.high, bar.low, bar.close) <= 0 or bar.volume < 0:
            anomalies.append(f"{bar.date}: non-positive price or negative volume")
            continue
        if bar.high < max(bar.open, bar.close, bar.low) or bar.low > min(bar.open, bar.close, bar.high):
            anomalies.append(f"{bar.date}: inconsistent OHLC range")
            continue
        if previous_close is not None and abs(bar.close / previous_close - 1) > max_daily_move:
            anomalies.append(f"{bar.date}: daily close move exceeds {max_daily_move:.0%}")
        clean.append(bar)
        previous_close = bar.close
    if len(clean) < len(bars):
        anomalies.append("One or more invalid rows were excluded")
    return clean, anomalies


def sma(values, period):
    if period <= 0 or len(values) < period:
        return None
    return sum(values[-period:]) / period


def rsi(values, period=14):
    if len(values) <= period:
        return None
    changes = [values[i] - values[i - 1] for i in range(len(values) - period, len(values))]
    gains = sum(max(change, 0) for change in changes) / period
    losses = sum(max(-change, 0) for change in changes) / period
    if losses == 0:
        return 100.0 if gains else 50.0
    return 100 - 100 / (1 + gains / losses)


def atr(bars, period=14):
    if len(bars) <= period:
        return None
    ranges = []
    for i in range(1, len(bars)):
        bar, previous = bars[i], bars[i - 1]
        ranges.append(max(bar.high - bar.low, abs(bar.high - previous.close), abs(bar.low - previous.close)))
    return sum(ranges[-period:]) / period


def market_regime(closes):
    short, long = sma(closes, 20), sma(closes, 50)
    if short is None or long is None:
        return "INSUFFICIENT_DATA"
    if short > long * 1.01:
        return "UPTREND"
    if short < long * 0.99:
        return "DOWNTREND"
    return "SIDEWAYS"


def fundamental_filter(fundamentals):
    """Conservative user-supplied data gate; missing/unverified values fail closed."""
    required = ("revenue_positive", "debt_to_equity", "data_verified")
    if not isinstance(fundamentals, dict) or any(key not in fundamentals for key in required):
        return {"status": "UNKNOWN", "reasons": ["Fundamental data is missing; no strategy signal"]}
    if fundamentals.get("data_verified") is not True or fundamentals.get("revenue_positive") is not True:
        return {"status": "FAIL", "reasons": ["Fundamentals are unverified or revenue is not positive"]}
    debt = fundamentals.get("debt_to_equity")
    if isinstance(debt, bool) or not isinstance(debt, (int, float)) or not isfinite(debt) or debt < 0:
        return {"status": "FAIL", "reasons": ["Debt-to-equity value is invalid"]}
    if debt > 0.30:
        return {"status": "FAIL", "reasons": ["Debt-to-equity exceeds the fixed 0.30 educational threshold"]}
    return {"status": "PASS", "reasons": []}


def strategy_signals(bars, fundamentals=None):
    """Four fixed educational signal rules; outputs are not orders or recommendations."""
    clean, anomalies = validate_bars(bars)
    closes = [bar.close for bar in clean]
    regime = market_regime(closes)
    gate = fundamental_filter(fundamentals)
    metrics = {"sma_20": sma(closes, 20), "sma_50": sma(closes, 50), "rsi_14": rsi(closes), "atr_14": atr(clean)}
    signals = {"sma_trend": "NO_SIGNAL", "rsi_reversion": "NO_SIGNAL", "breakout_20": "NO_SIGNAL", "trend_pullback": "NO_SIGNAL"}
    if len(closes) >= 50 and not anomalies and gate["status"] == "PASS":
        latest = closes[-1]
        prev_fast = sma(closes[:-1], 20)
        fast, slow = metrics["sma_20"], metrics["sma_50"]
        if fast > slow and prev_fast is not None and closes[-2] <= prev_fast:
            signals["sma_trend"] = "LONG_WATCH"
        if metrics["rsi_14"] is not None and metrics["rsi_14"] < 30:
            signals["rsi_reversion"] = "LONG_WATCH"
        if latest > max(closes[-21:-1]):
            signals["breakout_20"] = "LONG_WATCH"
        if regime == "UPTREND" and latest >= fast * 0.98 and latest <= fast * 1.01:
            signals["trend_pullback"] = "LONG_WATCH"
    return {
        "regime": regime,
        "fundamental_filter": gate,
        "metrics": metrics,
        "signals": signals,
        "anomalies": anomalies,
        "disclaimer": "تعليم فقط؛ ليست توصية أو أمراً. لا يوجد تنفيذ تداول.",
    }
