"""Kill-switch and risk request checks. No broker access is present."""

from pathlib import Path


def emergency_stop_enabled(kill_file):
    return Path(kill_file).is_file()


def validate_risk_request(cash, quantity, price, position_fraction=0.10,
                          stop_loss_fraction=0.08):
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0
           for value in (cash, quantity, price)):
        return {"accepted": False, "reason": "Invalid positive numeric input"}
    notional = quantity * price
    if notional > cash * position_fraction:
        return {"accepted": False, "reason": "Position exceeds fixed 10% of cash"}
    if stop_loss_fraction <= 0 or stop_loss_fraction > 0.08:
        return {"accepted": False, "reason": "Stop-loss limit is outside the fixed range"}
    return {"accepted": True, "reason": "Within local educational risk limits", "notional": notional}
