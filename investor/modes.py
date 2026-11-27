from pathlib import Path

MODES = ("DRY-RUN", "LIVE-CONFIRM", "AUTO")


def validate_transition(current, target, checks):
    """State-machine guard. AUTO is intentionally disabled in phase 4 until audited."""
    if target not in MODES:
        return {"accepted": False, "reason": "Unknown mode"}
    if target == current:
        return {"accepted": True, "reason": "Mode unchanged"}
    if target == "AUTO":
        return {"accepted": False, "reason": "AUTO requires external audited approval and is disabled"}
    if current == "DRY-RUN" and target == "LIVE-CONFIRM":
        required = ("explicit_confirmation", "kill_switch_clear", "broker_reconciliation",
                    "daily_loss_limit", "position_limit", "allowlist_verified")
        missing = [name for name in required if checks.get(name) is not True]
        if missing:
            return {"accepted": False, "reason": "Missing checks: " + ", ".join(missing)}
    if Path(checks.get("kill_file", "KILL")).is_file():
        return {"accepted": False, "reason": "Kill switch is active"}
    return {"accepted": True, "reason": "Transition accepted"}
