#!/usr/bin/env python3
"""
Restore .openclaw ← select version from GitHub → decrypt and replace
"""

import sys
import subprocess
import shutil
from pathlib import Path
from config import get_config

RESTORE_DIR = Path.home() / ".openclaw"
TEMP_DIR = Path.home() / "openclaw-transport-temp"


def human_size(path: Path) -> str:
    size = path.stat().st_size
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main():
    config = get_config()
    repo_url = config["REPO_URL"]
    password = config["BACKUP_PASSWORD"]

    # clone repo
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    print("Cloning backup repo...")
    result = subprocess.run(
        ["git", "clone", "--quiet", repo_url, str(TEMP_DIR)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("Clone failed:", result.stderr.strip())
        sys.exit(1)

    try:
        # list backups
        backups = sorted(
            (TEMP_DIR / "backups").glob("openclaw-*.tgz.gpg"), reverse=True
        )
        if not backups:
            print("No backups found in repo")
            sys.exit(1)

        print(f"\nAvailable versions ({len(backups)}):")
        print("-" * 50)
        for i, f in enumerate(backups, 1):
            size = human_size(f)
            label = " ← latest" if i == 1 else ""
            print(f"  [{i}] {f.name}  ({size}){label}")
        print("-" * 50)

        # pick version
        choice = input("\nSelect version [1] or press Enter for latest: ").strip()
        if not choice:
            chosen = backups[0]
        else:
            try:
                chosen = backups[int(choice) - 1]
            except (ValueError, IndexError):
                print("Invalid selection")
                sys.exit(1)

        print(f"\nRestoring: {chosen.name}")

        # extract on top of existing .openclaw (adds/overwrites, doesn't delete)
        RESTORE_DIR.mkdir(parents=True, exist_ok=True)

        # decrypt and extract
        gpg = subprocess.Popen(
            ["gpg", "--batch", "--yes", "--passphrase", password,
             "--decrypt", str(chosen)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        tar = subprocess.Popen(
            ["tar", "xzf", "-", "-C", str(RESTORE_DIR)],
            stdin=gpg.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        gpg.stdout.close()
        tar.communicate()

        if gpg.wait() != 0:
            print("Decryption failed — wrong password?")
            sys.exit(1)
        if tar.returncode != 0:
            print("Extraction failed")
            sys.exit(1)

        print(f"Restored .openclaw from {chosen.name}")

    finally:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()