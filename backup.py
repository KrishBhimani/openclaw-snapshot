#!/usr/bin/env python3
"""
Backup .openclaw → encrypted .tgz.gpg → push to GitHub with timestamp
"""

import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from config import get_config

SOURCE_DIR = Path.home() / ".openclaw"
BACKUP_REPO = Path.home() / "openclaw-transport"

EXCLUDE = [
    "backups-repo", ".git", ".env", "node_modules",
    "*.sock", "whatsapp/store/sessions-*", "credentials/whatsapp",
]


def main():
    if not SOURCE_DIR.is_dir():
        print(f"Error: {SOURCE_DIR} not found")
        sys.exit(1)

    config = get_config()
    password = config["BACKUP_PASSWORD"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backups_dir = BACKUP_REPO / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backups_dir / f"openclaw-{timestamp}.tgz.gpg"

    # tar | gpg
    print(f"Creating backup: {backup_file.name}")
    exclude_flags = []
    for p in EXCLUDE:
        exclude_flags += ["--exclude", p]

    tar = subprocess.Popen(
        ["tar", "czf", "-", *exclude_flags, "-C", str(SOURCE_DIR), "."],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    gpg = subprocess.Popen(
        ["gpg", "--batch", "--yes", "--passphrase", password,
         "--symmetric", "--cipher-algo", "AES256", "-o", str(backup_file)],
        stdin=tar.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    tar.stdout.close()
    gpg.communicate()

    if tar.wait() != 0 or gpg.returncode != 0:
        print("Error: backup creation failed")
        sys.exit(1)

    size = backup_file.stat().st_size / 1024
    print(f"Backup created: {backup_file.name} ({size:.1f} KB)")

    # push to github
    os.chdir(BACKUP_REPO)
    subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)

    if diff.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"backup: {timestamp}", "--quiet"],
                       check=True, capture_output=True)
        result = subprocess.run(["git", "push", "origin", "main", "--quiet"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("Pushed to GitHub")
        else:
            print("Push failed:", result.stderr.strip())
            sys.exit(1)
    else:
        print("No changes to push")

    print(f"Backup complete: {timestamp}")


if __name__ == "__main__":
    main()