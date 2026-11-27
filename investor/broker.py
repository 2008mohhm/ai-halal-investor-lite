import os


def load_broker_config():
    """Load secrets only; no key is committed and no network client is created."""
    return {
        "enabled": os.environ.get("BROKER_ENABLED", "0") == "1",
        "api_key": os.environ.get("BROKER_API_KEY"),
        "api_secret": os.environ.get("BROKER_API_SECRET"),
        "base_url": os.environ.get("BROKER_BASE_URL"),
    }


def safe_broker_status():
    config = load_broker_config()
    return {
        "enabled": config["enabled"],
        "configured": bool(config["api_key"] and config["api_secret"]),
        "key_source": "environment",
        "network_client": False,
    }
