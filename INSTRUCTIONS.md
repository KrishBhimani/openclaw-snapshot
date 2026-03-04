# OpenClaw Backup & Restore — Step by Step Guide

This guide will help you **backup** your OpenClaw agent and **restore** it on another workspace. No advanced tech knowledge required — just follow the steps in order.

---

## What Do These Scripts Do?

- **backup.py** — Takes a snapshot of your entire OpenClaw agent (the `.openclaw` folder), encrypts it with a password, and uploads it to a private GitHub repository. Each backup is saved with a timestamp so you can track versions.

- **restore.py** — Downloads your backups from GitHub, lets you pick which version you want, decrypts it, and sets up your `.openclaw` folder. Your agent is back, exactly how it was.

- **setup.py** — Sets up dependencies and connects to your GitHub repo. Safe to run multiple times.

Think of it like saving and loading a game — **backup** saves your progress, **restore** loads it on any machine.

---

## Folder Structure

Everything lives in one folder:

```
/home/coder/openclaw-backup/
├── .env.example        ← template (shows what keys you need)
├── .env                ← your actual keys (you create this)
├── config.py           ← shared config loader (don't edit)
├── setup.py            ← run to set things up / sync backups
├── backup.py           ← run to take a backup
├── restore.py          ← run to restore a version
└── instructions.md     ← this file
```

All your keys (password, GitHub token) live in the `.env` file — one place, easy to manage.

---

## Before You Start (One-Time Setup)

### Step 1 — Install GPG (encryption tool)

Run this in your terminal:

```bash
sudo apt-get update && sudo apt-get install -y gnupg gpg-agent
```

This installs the tool that encrypts and decrypts your backups. You need to run this on **every new workspace** before using backup or restore.

### Step 2 — Create a GitHub repo

1. Go to [github.com/new](https://github.com/new)
2. Name it `openclaw-transport`
3. Set it to **Private**
4. Click **Create repository**

### Step 3 — Create a GitHub PAT token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (fine-grained)"**
3. Give it a name like `openclaw-backup`
4. Select the **`repo`** scope (full control of private repositories)
5. Click **Generate token**
6. **Copy the token immediately** — GitHub will only show it once

### Step 4 — Fill in your .env file

```bash
cd /home/coder/openclaw-backup
cp .env.example .env
```

Now open `.env` in any editor and fill in your values:

```
BACKUP_PASSWORD=your-strong-password-here
GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=YourGitHubUsername
REPO_NAME=openclaw-transport
```

**Choose a strong backup password and remember it** — you'll need it if you ever restore on a machine that doesn't have this `.env` file.

### Step 5 — Run setup

```bash
python3 /home/coder/openclaw-backup/setup.py
```

You'll see:

```
==================================================
  OpenClaw Backup — One-Time Setup
==================================================

✓ Config loaded from .env
  GitHub user: YourUsername
  Repo: openclaw-transport

[1/2] Checking GPG...
✓ GPG installed

[2/2] Setting up GitHub transport repo...
✓ Repo cloned

==================================================
  Setup complete!
==================================================
```

Done. You're ready to backup and restore.

---

## How to Take a Backup

Make sure GPG is installed first (if on a new workspace):

```bash
sudo apt-get update && sudo apt-get install -y gnupg gpg-agent
```

Then run:

```bash
python3 /home/coder/openclaw-backup/backup.py
```

**What happens:**

1. It pulls the latest from GitHub (so existing backups from other workspaces are preserved)
2. Your `.openclaw` folder gets compressed and encrypted
3. The encrypted file is saved with a timestamp (e.g. `openclaw-20260227-120000.tgz.gpg`)
4. It gets pushed to your private GitHub repo

You'll see:

```
Syncing with GitHub...
Creating backup: openclaw-20260227-120000.tgz.gpg
Backup created: openclaw-20260227-120000.tgz.gpg (1542.3 KB)
Pushed to GitHub
Backup complete: 20260227-120000
```

**Tip:** Run this before making big changes to your agent, or at the end of each day.

---

## How to Restore

Make sure GPG is installed first (if on a new workspace):

```bash
sudo apt-get update && sudo apt-get install -y gnupg gpg-agent
```

### Restoring on a new workspace

On a new machine, you need the `openclaw-backup` folder with your `.env` file. Either:

- Copy the folder from your old workspace, or
- Clone/download it and create a fresh `.env` with your keys

Then run:

```bash
python3 /home/coder/openclaw-backup/restore.py
```

### What happens:

1. The script downloads your backups from GitHub
2. You see a list of all saved versions:

```
Available versions (4):
--------------------------------------------------
  [1] openclaw-20260227-120000.tgz.gpg  (1542.3 KB) ← latest
  [2] openclaw-20260226-090000.tgz.gpg  (1510.1 KB)
  [3] openclaw-20260225-150000.tgz.gpg  (1498.7 KB)
  [4] openclaw-20260225-103000.tgz.gpg  (1480.2 KB)
--------------------------------------------------

Select version [1] or press Enter for latest:
```

3. Press **Enter** for the latest, or type a number to pick a specific version
4. The script decrypts and extracts into your `.openclaw` folder (existing files not in the backup are left untouched)
5. Temporary files are cleaned up automatically

---

## Syncing Backups from Other Workspaces

If you backed up from a different workspace and your local `openclaw-transport` folder doesn't have the latest backups, just run setup again:

```bash
python3 /home/coder/openclaw-backup/setup.py
```

This is safe to run anytime — it will pull the latest backups from GitHub without deleting anything. After syncing, you can run `backup.py` or `restore.py` as normal.

---

## Setting Up on a New Workspace (Quick Checklist)

When you move to a fresh workspace, here's everything you need to do in order:

1. Copy the `openclaw-backup` folder to the new workspace (or recreate it with your `.env`)
2. Install GPG:
   ```bash
   sudo apt-get update && sudo apt-get install -y gnupg gpg-agent
   ```
3. Run setup (clones your backups from GitHub):
   ```bash
   python3 /home/coder/openclaw-backup/setup.py
   ```
4. Restore your agent:
   ```bash
   python3 /home/coder/openclaw-backup/restore.py
   ```

That's it — your agent is running on the new workspace.

---

## Where Are My Backups Stored?

On GitHub, your `openclaw-transport` repo looks like this:

```
openclaw-transport/
└── backups/
    ├── openclaw-20260225-103000.tgz.gpg
    ├── openclaw-20260225-150000.tgz.gpg
    ├── openclaw-20260226-090000.tgz.gpg
    └── openclaw-20260227-120000.tgz.gpg
```

Each file is a full encrypted snapshot. The timestamp tells you when it was taken (UTC time).

---

## Quick Reference

| I want to...                        | Run this                                          |
|-------------------------------------|---------------------------------------------------|
| Install GPG (every new workspace)   | `sudo apt-get update && sudo apt-get install -y gnupg gpg-agent` |
| First-time setup / sync backups     | `python3 /home/coder/openclaw-backup/setup.py`    |
| Take a backup                       | `python3 /home/coder/openclaw-backup/backup.py`   |
| Restore a version                   | `python3 /home/coder/openclaw-backup/restore.py`  |
| Restart after restore               | `openclaw gateway restart`                         |

---

## Troubleshooting

**"Error: .env file not found"**
→ You haven't created the `.env` file yet. Run `cp .env.example .env` and fill in your values.

**"Error: Missing values in .env file"**
→ Open your `.env` file and make sure `BACKUP_PASSWORD`, `GITHUB_PAT`, and `GITHUB_USERNAME` all have values.

**"Clone failed" during restore**
→ Your PAT token or username is wrong. Double-check both in `.env`. Make sure the token hasn't expired.

**"Decryption failed — wrong password?"**
→ The `BACKUP_PASSWORD` in your `.env` doesn't match the one used when the backup was created.

**"No backups found in repo"**
→ You haven't taken any backups yet, or you're pointing to the wrong repo.

**"Error: backup creation failed"**
→ GPG is probably not installed. Run `sudo apt-get update && sudo apt-get install -y gnupg gpg-agent` and try again.

**Push failed during backup**
→ Check your internet connection. Make sure your PAT token has `repo` scope and hasn't expired.

**Backup deleted old versions from GitHub**
→ Run `python3 /home/coder/openclaw-backup/setup.py` first to sync existing backups locally before running `backup.py`.

---

## Important Notes

- **All your keys live in `.env`.** This is the only file you need to keep safe. Don't share it or commit it to a public repo.
- **Backups are encrypted.** Without your password, nobody can read them — not even someone with access to your GitHub repo.
- **Each backup is a full snapshot**, not just the changes. They can get large over time.
- **Restore does not delete existing files.** It extracts on top of your `.openclaw` folder — files from the backup get added or overwritten, but anything not in the backup stays untouched.
- **WhatsApp sessions** are not included in backups (they're workspace-specific). You'll need to reconnect WhatsApp after restoring on a new machine.
- **Install GPG on every new workspace** before running backup or restore.
- **Run setup.py to sync** if you've backed up from another workspace and need those backups available locally.