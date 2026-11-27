"""Generate deterministic Arabic text reports from stored bars."""

from .analysis import strategy_signals


def report_for_symbol(symbol, bars, fundamentals=None):
    analysis = strategy_signals(bars, fundamentals)
    return {
        "symbol": symbol,
        "regime": analysis["regime"],
        "fundamental_status": analysis["fundamental_filter"]["status"],
        "signals": analysis["signals"],
        "anomalies": analysis["anomalies"],
        "metrics": analysis["metrics"],
        "disclaimer": analysis["disclaimer"],
    }


def arabic_summary(report):
    return (f"رمز {report['symbol']} — حالة السوق: {report['regime']}. "
            f"مرشح الأساسيات: {report['fundamental_status']}. "
            f"لا توجد أوامر تداول في هذه المرحلة.")
