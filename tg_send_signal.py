"""
tg_send_signal.py
-----------------
Called by GitHub Actions (send_signal run_type) to:
  1. Run the V17 signal command with fresh data
  2. Build a clean Telegram message from the written JSON/CSV files
  3. Send it to Telegram

Required env vars:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""

import csv
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
# Build clean Telegram message from model output files
# ---------------------------------------------------------------------------

def _pct(v) -> str:
    try:
        n = float(v) * 100
        return f"{'+' if n >= 0 else ''}{n:.1f}%"
    except Exception:
        return "n/a"


def _sh(v) -> str:
    try:
        return f"{float(v):.2f}"
    except Exception:
        return "n/a"


def _eq(v) -> str:
    try:
        return f"{float(v):,.2f}"
    except Exception:
        return "n/a"


def build_message() -> str:
    """
    Reads live_tracker/live_summary.json, live_signal_ledger.csv,
    and live_signal_periods.csv to produce a clean, mobile-friendly
    Telegram message. Never raises.
    """
    SEP = "-" * 32

    # --- live_summary.json ---
    try:
        with open("live_tracker/live_summary.json", "r", encoding="utf-8") as f:
            summary = json.load(f)
    except Exception as e:
        return f"Could not read live_summary.json: {e}"

    # --- live_signal_ledger.csv (latest signal details) ---
    latest_ledger = {}
    try:
        with open("live_tracker/live_signal_ledger.csv", "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            if rows:
                latest_ledger = rows[-1]
    except Exception:
        pass

    # --- live_signal_periods.csv (current period P&L) ---
    open_period = {}
    pending_period = {}
    try:
        with open("live_tracker/live_signal_periods.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("status") == "OPEN":
                    open_period = row
                elif row.get("status") == "PENDING_EXECUTION":
                    pending_period = row
    except Exception:
        pass

    lines = []

    # ── Signal block ──────────────────────────────────────
    last_data  = summary.get("last_data_date", "?")
    alloc      = summary.get("latest_target_allocation", "n/a")
    regime     = latest_ledger.get("regime", "?")
    sig_val    = latest_ledger.get("v17_signal", "?")
    status     = latest_ledger.get("status", "")
    trade_date = latest_ledger.get("actual_trade_date") or \
                 latest_ledger.get("estimated_trade_date") or "pending"
    reason_raw = latest_ledger.get("reason", "")
    # Truncate reason at first semicolon for brevity
    reason = reason_raw.split(";")[0].strip() if reason_raw else ""

    lines.append(f"V17 SIGNAL — {last_data}")
    lines.append(SEP)
    lines.append(f"Hold:    {alloc}")
    lines.append(f"Regime:  {regime}  ({sig_val}x)")
    if reason:
        lines.append(f"Note:    {reason}")
    lines.append(f"Trade:   {trade_date}  [{status}]")

    # ── Live tracker block ────────────────────────────────
    start_dt  = summary.get("start_signal_date", "?")
    m_ret     = _pct(summary.get("model_total_return"))
    s_ret     = _pct(summary.get("spy_total_return"))
    excess    = _pct(summary.get("excess_return"))
    m_sharpe  = _sh(summary.get("model_sharpe"))
    s_sharpe  = _sh(summary.get("spy_sharpe"))
    m_dd      = _pct(summary.get("model_max_drawdown"))
    s_dd      = _pct(summary.get("spy_max_drawdown"))
    equity    = _eq(summary.get("model_equity"))

    lines.append("")
    lines.append(f"LIVE TRACKER  ({start_dt} to {last_data})")
    lines.append(SEP)
    lines.append(f"{'':8s}  {'Return':>7}  {'Sharpe':>6}  {'MaxDD':>7}")
    lines.append(f"{'Model':8s}  {m_ret:>7}  {m_sharpe:>6}  {m_dd:>7}")
    lines.append(f"{'SPY':8s}  {s_ret:>7}  {s_sharpe:>6}  {s_dd:>7}")
    lines.append(f"{'Excess':8s}  {excess:>7}")
    lines.append(f"Equity:   {equity} USD")

    # ── Current / open period ─────────────────────────────
    if open_period:
        pd_start  = open_period.get("trade_date", "?")
        pd_regime = open_period.get("regime", "?")
        pd_sig    = open_period.get("v17_signal", "?")
        pd_model  = _pct(open_period.get("model_period_return"))
        pd_spy    = _pct(open_period.get("spy_period_return"))
        pd_exc    = _pct(open_period.get("excess_return"))

        lines.append("")
        lines.append(f"CURRENT PERIOD  ({pd_start} -> open)")
        lines.append(SEP)
        lines.append(f"{pd_regime}  |  {pd_sig}x")
        lines.append(f"Model: {pd_model}   SPY: {pd_spy}   Excess: {pd_exc}")

    # ── Next / pending signal ─────────────────────────────
    if pending_period:
        next_trade  = pending_period.get("trade_date", "pending")
        next_regime = pending_period.get("regime", "?")
        next_sig    = pending_period.get("v17_signal", "?")
        next_alloc  = pending_period.get("target_allocation", alloc)

        lines.append("")
        lines.append(f"NEXT SIGNAL  (trade: {next_trade})")
        lines.append(SEP)
        lines.append(f"{next_regime}  |  {next_sig}x")
        lines.append(f"Allocation: {next_alloc}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fallback: extract raw sections from terminal output
# ---------------------------------------------------------------------------

def extract_fallback(output: str) -> str:
    """Used only if build_message() fails — strips === headers and noise."""
    lines = output.split("\n")
    out = []
    capturing = False

    for line in lines:
        stripped = line.strip()

        if "V17 SIGNAL" in line and "===" in line:
            capturing = True
            import re
            m = re.search(r"\((\d{4}-\d{2}-\d{2})\)", line)
            out.append(f"V17 SIGNAL — {m.group(1) if m else ''}")
            continue

        if "LIVE TRACKER" in line and "===" in line:
            capturing = True
            out.append("")
            out.append("LIVE TRACKER")
            continue

        if capturing:
            # Skip noise lines
            if any(x in line for x in ["Action:", "Report:", "/home/runner", "/runner/"]):
                continue
            # Skip long === dividers
            if stripped.startswith("=") and stripped.endswith("=") and len(stripped) >= 20:
                continue
            # Shorten long --- separators
            if stripped.startswith("-") and stripped == "-" * len(stripped) and len(stripped) > 20:
                out.append("-" * 28)
                continue
            out.append(line.rstrip())

    result = "\n".join(out).strip()
    return result if result else output.strip()[-3000:]


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

    # Try clean JSON-based message first, fall back to terminal extraction
    try:
        msg = build_message()
    except Exception as e:
        print(f"build_message failed: {e} — falling back to extraction", file=sys.stderr)
        msg = extract_fallback(proc.stdout)

    if not msg or not msg.strip():
        msg = "Signal ran but produced no readable output. Check GitHub Actions logs."

    ok = tg_send(bot_token, chat_id, msg)
    if ok:
        print("Telegram message sent successfully.", flush=True)
    else:
        print("WARNING: Telegram send may have failed.", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Top-level guard — any crash sends error to Telegram
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
