"""Offline tests for phase 3. No market data or brokerage calls."""

from investor.backtest import buy_and_hold, simple_backtest
from investor.risk import emergency_stop_enabled, validate_risk_request


def test_buy_and_hold_comparison():
    assert buy_and_hold([100, 110], 10_000)["return_pct"] == 10


def test_fixed_risk_rejects_oversized_position():
    accepted = validate_risk_request(10_000, 10, 100)
    assert accepted["accepted"]
    rejected = validate_risk_request(10_000, 20, 100)
    assert not rejected["accepted"]


def test_kill_switch(tmp_path):
    kill = tmp_path / "KILL"
    assert not emergency_stop_enabled(kill)
    kill.touch()
    assert emergency_stop_enabled(kill)


def test_backtest_is_out_of_sample_and_has_benchmark():
    bars = []
    from investor.analysis import Bar
    for i in range(100):
        bars.append(Bar(f"2025-{i // 28 + 1:02d}-{i % 28 + 1:02d}", 100+i*.2, 101+i*.2, 99+i*.2, 100+i*.2, 1000))
    result = simple_backtest(bars)
    assert result["status"] == "OK"
    assert result["train_rows"] == 75
    assert result["test_rows"] == 25
    assert "benchmark_return_pct" in result
