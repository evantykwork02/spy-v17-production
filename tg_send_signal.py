"""
tg_send_signal.py
-----------------
Called by GitHub Actions (send_signal run_type) to:
  1. Run the V17 signal command with fresh data
  2. Extract the V17 SIGNAL + LIVE TRACKER sections from the output
  3. Send them to Telegram

Required env vars (set as GitHub Actions secrets):
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""

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
# Extract V17 SIGNAL + LIVE TRACKER sections from terminal output
# ---------------------------------------------------------------------------

def extract_key_sections(output: str) -> str:
    """
    Pulls the V17 SIGNAL block (regime/allocation/note) and the
    LIVE TRACKER block (P&L table, current period, next signal).
    Skips POSITION SIZING and RECENT WEEKS (too long for Telegram).
    Always returns something non-empty.
    """
    lines = output.split("\n")
    signal_lines = []
    tracker_lines = []
    in_signal = False
    in_tracker = False

    for line in lines:
        stripped = line.strip()

        # Enter signal section
        if "V17 SIGNAL" in line and "===" in line:
            in_signal = True
            in_tracker = False
            signal_lines.append(line)
            continue

        # Exit signal section at next === header (not the signal header itself)
        if in_signal and stripped.startswith("=") and stripped.endswith("=") \
                and len(stripped) > 10 and "V17 SIGNAL" not in line:
            in_signal = False

        # Enter live tracker section
        if "LIVE TRACKER" in line and "===" in line:
            in_signal = False
            in_tracker = True
            tracker_lines.append("")
            tracker_lines.append(line)
            continue

        # Exit tracker at the final closing === divider
        if in_tracker and stripped == "=" * len(stripped) and len(stripped) >= 20:
            in_tracker = False
            tracker_lines.append(line)
            continue

        if in_signal:
            signal_lines.append(line)
        elif in_tracker:
            tracker_lines.append(line)

    result = "\n".join(signal_lines + tracker_lines).strip()

    # Fallback 1: return last 3000 chars if extraction found nothing
    if not result and output.strip():
        result = output.strip()[-3000:]

    # Fallback 2: nothing at all
    if not result:
        result = "Signal ran but produced no output. Check GitHub Actions logs."

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not bot_token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.", file=sys.stderr)
        sys.exit(1)

    cmd = [
        sys.executable,
        "spy_v17_conservative.py",
        "--mode", "signal",
        "--refresh-data",
        "--live-track",
    ]

    print(f"Running: {' '.join(cmd)}", flush=True)

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    # Always print output to the Actions log for debugging
    if proc.stdout:
        print(proc.stdout, flush=True)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, flush=True)

    if proc.returncode != 0:
        error_body = (proc.stderr or proc.stdout or "No output").strip()[-2000:]
        tg_send(bot_token, chat_id,
            f"V17 signal FAILED (exit {proc.returncode}):\n\n{error_body}"
        )
        sys.exit(proc.returncode)

    sections = extract_key_sections(proc.stdout)
    ok = tg_send(bot_token, chat_id, sections)

    if ok:
        print("Telegram message sent successfully.", flush=True)
    else:
        print("WARNING: Telegram send may have failed. Check logs.", file=sys.stderr, flush=True)
        sys.exit(1)


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
            tg_send(_bot, _chat, f"tg_send_signal.py crashed:\n\n{err[-2000:]}")
        sys.exit(1)
