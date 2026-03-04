"""
Shared config loader for OpenClaw backup scripts.
Reads .env file from the same directory as the calling script.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"


def load_env() -> dict:
    """Read .env file and return as dict."""
    if not ENV_FILE.is_file():
        print(f"Error: .env file not found at {ENV_FILE}")
        print(f"Run this first:  cp .env.example .env  (then fill in your values)")
        sys.exit(1)

    config = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


def get_config() -> dict:
    """Load and validate the config."""
    config = load_env()

    required = ["BACKUP_PASSWORD", "GITHUB_PAT", "GITHUB_USERNAME"]
    missing = [k for k in required if not config.get(k)]

    if missing:
        print("Error: Missing values in .env file:")
        for k in missing:
            print(f"  - {k}")
        sys.exit(1)

    config.setdefault("REPO_NAME", "openclaw-transport")
    config["REPO_URL"] = (
        f"https://{config['GITHUB_PAT']}@github.com/"
        f"{config['GITHUB_USERNAME']}/{config['REPO_NAME']}.git"
    )

    return config