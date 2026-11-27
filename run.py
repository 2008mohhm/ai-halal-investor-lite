from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

from investor import create_app

app = create_app(
    {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "local-development-only"),
        "DATABASE_PATH": os.environ.get("DATABASE_PATH", "instance/investor.sqlite3"),
        "WATCHLIST_PATH": os.environ.get("WATCHLIST_PATH", "config/watchlist.json"),
    }
)

if __name__ == "__main__":
    # Bind only to localhost; do not expose this development server to the network.
    app.run(host="127.0.0.1", port=5000, debug=False)
