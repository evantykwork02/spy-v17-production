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
import math
import os
import subprocess
import sys
import traceback

import requests

from runtime_config import DEFAULT_CURRENCY, load_runtime_config


# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

def tg_send(bot_token: str, chat_id: str, text: str) -> bool:
    """Send plain-text message (used for errors/fallback)."""
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


def tg_send_code(bot_token: str, chat_id: str, text: str) -> bool:
    """Send monospace HTML <pre> message (used for signal/tracker output)."""
    if not text or not text.strip():
        text = "(no output — check GitHub Actions logs)"
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if len(escaped) > 3900:
        escaped = escaped[:3900] + "\n...(truncated)"
    payload = f"<pre>{escaped}</pre>"
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": payload, "parse_mode": "HTML"},
            timeout=15,
        )
        if not resp.ok:
            print(f"Telegram API error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"Telegram send exception: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Formatting helpers — all percentages at 2 decimal places
# ---------------------------------------------------------------------------

def _pct(v) -> str:
    try:
        n = float(v) * 100
        return f"{'+' if n >= 0 else ''}{n:.2f}%"
    except Exception:
        return "n/a"


def _excess(model_v, spy_v) -> str:
    """Derives excess from the already-rounded display values so it always
    matches what you'd compute by subtracting the two displayed figures."""
    try:
        m = round(float(model_v) * 100, 2)
        s = round(float(spy_v)   * 100, 2)
        e = round(m - s, 2)
        return f"{'+' if e >= 0 else ''}{e:.2f}%"
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


def _get_usd_to_account_rate(currency: str) -> float:
    """
    Fetch current USD to account-currency exchange rate.

    Returns:
        Exchange rate (1 USD = X account currency)
    """
    currency = (currency or DEFAULT_CURRENCY).upper()
    if currency == "USD":
        return 1.0
    if currency != "SGD":
        return 1.0

    try:
        import yfinance as yf
        ticker = yf.Ticker("USDSGD=X")
        hist = ticker.history(period="1d")
        if not hist.empty:
            rate = float(hist["Close"].iloc[-1])
            return rate
    except Exception:
        pass
    return 1.34  # Fallback USD/SGD rate


def _get_current_prices(symbols: list) -> dict:
    """
    Fetch current prices for given symbols from Yahoo Finance (in USD).
    
    Returns:
        Dictionary mapping symbol -> price (in USD), or empty dict if fetch fails
    """
    try:
        import yfinance as yf
        prices = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                    prices[symbol] = price
            except Exception:
                continue
        return prices
    except Exception:
        return {}


def _parse_allocation_with_capital(alloc_str: str, equity: float, currency: str) -> str:
    """
    Parse allocation string like "SPY 90.0%, SPXL 10.0%" and calculate
    share counts based on equity in the configured account currency.

    Returns:
        Formatted string with share counts and percentages
        e.g., "SPY 9 shares (90.0%)  SPXL 3 shares (10.0%)"
    """
    try:
        currency = (currency or DEFAULT_CURRENCY).upper()
        equity = float(equity)
        if not alloc_str or alloc_str == "n/a" or equity <= 0:
            return alloc_str  # Guard: can't calculate with zero/negative equity
        
        # Extract symbols to fetch prices
        tokens = alloc_str.split(",")
        symbols = []
        for token in tokens:
            token = token.strip()
            if token:
                parts = token.split()
                if len(parts) >= 1:
                    symbols.append(parts[0])
        
        # Fetch current prices (in USD) and exchange rate
        prices_usd = _get_current_prices(symbols)
        usd_to_account = _get_usd_to_account_rate(currency)

        # Convert USD prices to account currency, filtering out zero/invalid prices
        prices_sgd = {}
        for symbol, price in prices_usd.items():
            try:
                price_sgd = float(price) * usd_to_account
                if price_sgd > 0:
                    prices_sgd[symbol] = price_sgd
            except (ValueError, TypeError):
                pass  # Skip invalid prices

        if not prices_sgd:
            # Fallback: return allocation with account-currency amounts if price fetch fails
            result_parts = []
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                parts = token.split()
                if len(parts) >= 2:
                    symbol = parts[0]
                    pct_str = parts[1].rstrip("%")
                    try:
                        pct = float(pct_str)
                        capital = equity * (pct / 100.0)
                        result_parts.append(f"{symbol} {pct:.1f}% ({currency} {capital:,.2f})")
                    except ValueError:
                        result_parts.append(token)
                else:
                    result_parts.append(token)
            return "  ".join(result_parts) if result_parts else alloc_str
        
        # Calculate share counts
        result_parts = []
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            parts = token.split()
            if len(parts) >= 2:
                symbol = parts[0]
                pct_str = parts[1].rstrip("%")
                try:
                    pct = float(pct_str)
                    if symbol in prices_sgd:
                        capital_sgd = equity * (pct / 100.0)
                        price_sgd = prices_sgd[symbol]
                        if price_sgd > 0:  # Guard against zero price
                            shares = capital_sgd / price_sgd
                            # Round down to be conservative (int() truncates)
                            shares_rounded = int(math.floor(shares))
                            result_parts.append(f"{symbol} {shares_rounded} shares ({pct:.1f}%)")
                        else:
                            result_parts.append(f"{symbol} {pct:.1f}%")
                    else:
                        result_parts.append(f"{symbol} {pct:.1f}%")
                except (ValueError, ZeroDivisionError):
                    result_parts.append(token)
            else:
                result_parts.append(token)
        
        return "  ".join(result_parts) if result_parts else alloc_str
    except Exception:
        return alloc_str


# ---------------------------------------------------------------------------
# Build clean Telegram message from model output files
# ---------------------------------------------------------------------------

def build_message() -> str:
    SEP = "-" * 36
    currency = load_runtime_config().currency

    # --- latest_signal.json (latest signal metadata) ---
    latest_signal = {}
    try:
        with open("outputs_v17_conservative/latest_signal.json", "r", encoding="utf-8") as f:
            latest_signal = json.load(f)
    except Exception:
        pass

    # --- live_summary.json ---
    try:
        with open("live_tracker/live_summary.json", "r", encoding="utf-8") as f:
            summary = json.load(f)
    except Exception as e:
        return f"Could not read live_summary.json: {e}"
    currency = str(summary.get("currency") or currency).upper()

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
    tracked_weeks = None
    pending_signal_weeks = None
    try:
        with open("live_tracker/live_signal_periods.csv", "r", encoding="utf-8") as f:
            period_rows = list(csv.DictReader(f))
            for row in period_rows:
                if row.get("status") == "OPEN":
                    open_period = row
                elif row.get("status") == "PENDING_EXECUTION":
                    pending_period = row
            tracked_weeks = sum(1 for row in period_rows if row.get("status") in {"CLOSED", "OPEN"})
            pending_signal_weeks = sum(1 for row in period_rows if row.get("status") == "PENDING_EXECUTION")
    except Exception:
        pass

    last_data  = summary.get("last_data_date", "?")
    alloc      = summary.get("latest_target_allocation", "n/a")
    regime     = latest_ledger.get("regime", "?")
    sig_val    = latest_ledger.get("v17_signal", "?")
    trade_date = (latest_ledger.get("actual_trade_date") or
                  latest_ledger.get("estimated_trade_date") or "pending")
    rf_pct     = latest_signal.get("risk_free_rate_annual_pct")
    rf_annual  = f"{float(rf_pct):.2f}%" if rf_pct is not None else "n/a"
    rf_date    = latest_signal.get("risk_free_rate_date", last_data)
    rf_source  = latest_signal.get("risk_free_rate_source", "n/a")

    lines = []

    # ── Signal block ──────────────────────────────────────
    lines.append(f"V17 SIGNAL — {last_data}")
    lines.append("=" * 36)
    # Parse allocation with capital amounts
    equity_value = summary.get("model_equity", 0)
    alloc_with_capital = _parse_allocation_with_capital(alloc, equity_value, currency)
    lines.append(f"Alloc:   {alloc_with_capital}")
    lines.append(f"Regime:  {regime}  ({sig_val}x)")
    lines.append(f"Trade:   {trade_date}")
    lines.append(f"RF 3M:   {rf_annual} annual  ({rf_date}, {rf_source})")

    # ── Tracker summary ───────────────────────────────────
    start_dt    = summary.get("start_signal_date", "?")
    m_ret_raw   = summary.get("model_total_return")
    s_ret_raw   = summary.get("spy_total_return")
    m_ret       = _pct(m_ret_raw)
    s_ret       = _pct(s_ret_raw)
    exc         = _excess(m_ret_raw, s_ret_raw)
    m_sh        = _sh(summary.get("model_sharpe"))
    s_sh        = _sh(summary.get("spy_sharpe"))
    m_dd        = _pct(summary.get("model_max_drawdown"))
    s_dd        = _pct(summary.get("spy_max_drawdown"))
    equity      = _eq(summary.get("model_equity"))
    if tracked_weeks is None:
        try:
            tracked_weeks = int(summary.get("tracked_weeks"))
        except Exception:
            tracked_weeks = None
    if pending_signal_weeks is None:
        try:
            pending_signal_weeks = int(summary.get("pending_signal_weeks"))
        except Exception:
            pending_signal_weeks = None

    lines.append("")
    lines.append(f"TRACKER  ({start_dt} to {last_data})")
    lines.append(SEP)
    lines.append(f"{'':8s}  {'Return':>7}  {'Sharpe':>6}  {'MaxDD':>7}")
    lines.append(f"{'Model':8s}  {m_ret:>7}  {m_sh:>6}  {m_dd:>7}")
    lines.append(f"{'SPY':8s}  {s_ret:>7}  {s_sh:>6}  {s_dd:>7}")
    lines.append(f"{'Excess':8s}  {exc:>7}")
    lines.append(f"Equity:   {equity} {currency}")
    if tracked_weeks is not None:
        weeks_line = f"Weeks:    {tracked_weeks} tracked"
        if pending_signal_weeks:
            weeks_line += f", {pending_signal_weeks} pending"
        lines.append(weeks_line)

    # ── Current / open period ─────────────────────────────
    if open_period:
        pd_start     = open_period.get("trade_date", "?")
        pd_model_raw = open_period.get("model_period_return")
        pd_spy_raw   = open_period.get("spy_period_return")
        pd_model     = _pct(pd_model_raw)
        pd_spy       = _pct(pd_spy_raw)
        pd_exc       = _excess(pd_model_raw, pd_spy_raw)

        lines.append("")
        lines.append(f"THIS PERIOD  ({pd_start} -> open)")
        lines.append(SEP)
        lines.append(f"Model: {pd_model}   SPY: {pd_spy}   Exc: {pd_exc}")

    # ── Next / pending signal ─────────────────────────────
    if pending_period:
        next_trade  = pending_period.get("trade_date", "pending")
        next_regime = pending_period.get("regime", "?")
        next_sig    = pending_period.get("v17_signal", "?")
        next_alloc  = pending_period.get("target_allocation", alloc)
        # Parse next allocation with share counts (using current equity)
        next_alloc_with_capital = _parse_allocation_with_capital(next_alloc, equity_value, currency)

        lines.append("")
        lines.append(f"NEXT WEEK  (trade: {next_trade})")
        lines.append(SEP)
        lines.append(f"{next_alloc_with_capital}")
        lines.append(f"{next_regime}  |  {next_sig}x")

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
            if any(x in line for x in ["Action:", "Report:", "/home/runner", "/runner/"]):
                continue
            if stripped.startswith("=") and stripped.endswith("=") and len(stripped) >= 20:
                continue
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

    try:
        msg = build_message()
    except Exception as e:
        print(f"build_message failed: {e} — falling back to extraction", file=sys.stderr)
        msg = extract_fallback(proc.stdout)

    if not msg or not msg.strip():
        msg = "Signal ran but produced no readable output. Check GitHub Actions logs."

    ok = tg_send_code(bot_token, chat_id, msg)
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
