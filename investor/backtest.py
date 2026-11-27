"""Backtesting and fixed risk controls; no broker or order implementation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestConfig:
    initial_cash: float = 10_000.0
    max_position_fraction: float = 0.10
    stop_loss_fraction: float = 0.08
    trailing_stop_fraction: float = 0.10


def buy_and_hold(closes, initial_cash):
    if not closes or initial_cash <= 0:
        return {"status": "INSUFFICIENT_DATA", "return_pct": 0.0}
    return {"status": "OK", "return_pct": (closes[-1] / closes[0] - 1) * 100}


def simple_backtest(bars, initial_cash=10_000.0, max_position_fraction=0.10,
                    stop_loss_fraction=0.08, trailing_stop_fraction=0.10):
    """Small out-of-sample daily backtest. Re-enters only on model selected dates."""
    if len(bars) < 60 or initial_cash <= 0:
        return {"status": "INSUFFICIENT_DATA", "total_return_pct": 0.0,
                "benchmark_return_pct": 0.0, "trades": 0}
    split = int(len(bars) * 0.75)
    train, test = bars[:split], bars[split:]
    if len(train) < 50 or len(test) < 10:
        return {"status": "INSUFFICIENT_DATA", "total_return_pct": 0.0,
                "benchmark_return_pct": 0.0, "trades": 0}
    cash, shares, stop, peak, trades = initial_cash, 0.0, None, None, 0
    for bar in test:
        if shares:
            peak = max(peak or bar.close, bar.close)
            stop = max(stop or 0.0, peak * (1 - trailing_stop_fraction))
            if bar.low <= stop:
                cash += shares * stop
                shares, stop, peak = 0.0, None, None
                trades += 1
            elif bar.close <= bar.close * (1 - stop_loss_fraction):
                pass
            continue
        previous = [b.close for b in train if b.date < bar.date][-20:]
        if len(previous) >= 20:
            fast = sum(previous[-20:]) / 20
            slow = sum([b.close for b in train if b.date < bar.date][-50:]) / 50 if len([b.close for b in train if b.date < bar.date]) >= 50 else None
            if slow is not None and fast > slow:
                shares = (cash * max_position_fraction) / bar.close
                cash -= shares * bar.close
                stop = bar.close * (1 - stop_loss_fraction)
                peak = bar.close
                trades += 1
    equity = cash + shares * test[-1].close
    benchmark = buy_and_hold([b.close for b in test], initial_cash)
    return {"status": "OK", "total_return_pct": (equity / initial_cash - 1) * 100,
            "benchmark_return_pct": benchmark["return_pct"], "trades": trades,
            "train_rows": len(train), "test_rows": len(test),
            "disclaimer": "تعليمي؛ لا يعتبر أداء تاريخياً ضماناً للمستقبل."}
