"""
inject_capital.py
-----------------
Called by GitHub Actions (capital_inject run_type) to:
  1. Add a capital injection entry to config.json
  2. Commit and push config.json to the repo
  3. If the injection date is today or past, re-run the signal to apply it
     immediately and commit the updated tracker files
  4. Send a confirmation to Telegram

Required env vars (set as GitHub Actions secrets / step env):
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
  INJECT_AMOUNT    — numeric amount (in the currency set in config.json)
  INJECT_DATE      — YYYY-MM-DD date string
"""

import datetime
import json
import os
import subprocess
import sys
import traceback

import requests


# ---------------------------------------------------------------------------
# Telegram — never raises, never sends empty messages
# ---------------------------------------------------------------------------

def tg_send(bot_token: str, chat_id: str, text: str) -> bool:
    """Send a Telegram message. Returns True on success. Never raises."""
    if not text or not text.strip():
        text = "(no output — check GitHub Actions logs)"
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
    success = True
    for chunk in chunks:
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": chunk},
                timeout=15,
            )
            if not resp.ok:
                print(f"Telegram API error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
                success = False
        except Exception as e:
            print(f"Telegram send exception: {e}", file=sys.stderr)
            success = False
    return success


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git(*args: str) -> None:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed (exit {result.returncode}):\n"
            f"{result.stderr.strip() or result.stdout.strip()}"
        )


def git_setup() -> None:
    git("config", "user.email", "github-actions[bot]@users.noreply.github.com")
    git("config", "user.name", "github-actions[bot]")


def has_staged_changes() -> bool:
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    return result.returncode != 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not bot_token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.", file=sys.stderr)
        sys.exit(1)

    raw_amount = os.environ.get("INJECT_AMOUNT", "").strip()
    date_str   = os.environ.get("INJECT_DATE", "").strip()

    # --- Validate inputs ---
    try:
        amount = float(raw_amount)
        assert amount > 0
    except (ValueError, AssertionError):
        tg_send(bot_token, chat_id,
            f"Capital injection failed: invalid amount '{raw_amount}'.\n"
            "Send: inject <positive number> [YYYY-MM-DD]"
        )
        sys.exit(1)

    if not date_str or not _valid_date(date_str):
        tg_send(bot_token, chat_id,
            f"Capital injection failed: invalid date '{date_str}'.\n"
            "Date must be YYYY-MM-DD."
        )
        sys.exit(1)

    # --- Read config.json ---
    with open("config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    injections: list = cfg.get("capital_injections", [])
    currency: str    = cfg.get("currency", "USD")

    # --- Check for duplicate on same date ---
    for inj in injections:
        if inj.get("date") == date_str:
            tg_send(bot_token, chat_id,
                f"Injection on {date_str} already exists "
                f"(amount: {inj['amount']} {currency}).\n\n"
                "Edit config.json on GitHub directly to change it."
            )
            sys.exit(0)

    # --- Add new injection, keep chronological order ---
    injections.append({"date": date_str, "amount": amount})
    injections.sort(key=lambda x: x["date"])
    cfg["capital_injections"] = injections

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")

    # --- Commit config.json ---
    git_setup()
    git("add", "config.json")
    git("commit", "-m",
        f"Capital injection: +{amount} {currency} on {date_str} [via Telegram]"
    )
    git("push")
    print(f"config.json committed and pushed.", flush=True)

    # --- If injection date is today or past, run signal now ---
    today = datetime.date.today().isoformat()

    if date_str <= today:
        print("Injection date is today or past — running signal now.", flush=True)

        proc = subprocess.run(
            [sys.executable, "spy_v17_conservative.py",
             "--mode", "signal", "--refresh-data", "--live-track"],
            capture_output=True, text=True, timeout=600,
        )

        if proc.stdout:
            print(proc.stdout, flush=True)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr, flush=True)

        # Commit updated live_tracker files if changed
        subprocess.run(["git", "add", "live_tracker/"], check=False)
        if has_staged_changes():
            git("commit", "-m",
                f"Update tracker after capital injection {date_str} [via Telegram]"
            )
            git("push")
            print("Tracker committed and pushed.", flush=True)

        if proc.returncode != 0:
            tg_send(bot_token, chat_id,
                f"Injection saved to config, but signal run failed "
                f"(exit {proc.returncode}).\n\n"
                f"{(proc.stderr or proc.stdout or 'No output').strip()[-1000:]}"
            )
            sys.exit(proc.returncode)
        else:
            tg_send(bot_token, chat_id,
                f"Capital injection applied and tracker updated.\n\n"
                f"Amount:  +{amount} {currency}\n"
                f"Date:    {date_str}\n\n"
                "Send 'status' to see updated equity."
            )
    else:
        tg_send(bot_token, chat_id,
            f"Capital injection scheduled.\n\n"
            f"Amount:  +{amount} {currency}\n"
            f"Date:    {date_str}\n\n"
            f"Will be applied automatically when the signal runs on or after {date_str}."
        )


def _valid_date(s: str) -> bool:
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Top-level guard — any unhandled crash sends an error to Telegram
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _bot  = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    _chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    try:
        main()
    except Exception:
        err = traceback.format_exc()
        print(err, file=sys.stderr, flush=True)
        if _bot and _chat:
            tg_send(_bot, _chat, f"inject_capital.py crashed:\n\n{err[-2000:]}")
        sys.exit(1)
