"""Phase 4 orchestration without execution or AI decision-making."""

import json
import os
from pathlib import Path

from .modes import validate_transition


def reconcile_placeholder(broker_state, local_state):
    """Explicitly represent unverified reconciliation; never authorizes a trade."""
    return {"matched": False, "reason": "Broker reconciliation is not implemented", 
            "broker": broker_state, "local": local_state}


def termux_notify(message, enabled=None):
    enabled = enabled if enabled is not None else os.environ.get("TERMUX_NOTIFICATIONS", "0") == "1"
    if not enabled:
        return {"sent": False, "reason": "Termux notifications disabled"}
    if not os.path.exists("/data/data/com.termux/files/usr/bin/termux-notification"):
        return {"sent": False, "reason": "termux-notification unavailable"}
    return {"sent": False, "reason": "Notification transport disabled in phase 4"}
