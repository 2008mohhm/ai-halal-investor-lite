"""Offline tests for mode and broker safety."""

from investor.broker import safe_broker_status
from investor.modes import validate_transition


def test_mode_defaults_and_auto_stays_disabled(tmp_path):
    assert validate_transition("DRY-RUN", "AUTO", {"kill_file": str(tmp_path / "KILL")})["accepted"] is False


def test_live_confirm_requires_checks(tmp_path):
    result = validate_transition("DRY-RUN", "LIVE-CONFIRM", {"kill_file": str(tmp_path / "KILL")})
    assert result["accepted"] is False


def test_no_broker_secrets_or_network_is_exposed(monkeypatch):
    monkeypatch.setenv("BROKER_ENABLED", "1")
    status = safe_broker_status()
    assert status["network_client"] is False
    assert status["key_source"] == "environment"


def test_app_stays_non_trading(tmp_path):
    from investor import create_app
    app = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db")})
    health = app.test_client().get("/health")
    assert health.status_code == 200
    assert health.json["trading_enabled"] is False
    assert health.json["mode"] == "DRY-RUN"
