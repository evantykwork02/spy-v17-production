"""
V17 live paper tracker.

This module is intentionally separate from the core model logic. It keeps a
duplicate-safe ledger of completed Friday signals, then reconstructs a live-paper
portfolio from the exact target weights produced by the model.

Important execution convention:
    The tracker matches the core backtest convention: a Friday signal becomes
    effective on the next available trading day's close-to-close return. If you
    trade Monday using the Friday signal, this is the cleanest comparable paper
    tracking assumption without intraday open-price data.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from spy_v17_conservative import (
    ASSETS,
    allocation_text,
    fmt_num,
    fmt_pct,
    fmt_pct_signed,
    get_rf_daily,
    metrics_daily,
    _markdown_table,
)


def _json_safe(x):
    if isinstance(x, (np.floating, float)):
        return None if pd.isna(x) else float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (pd.Timestamp,)):
        return x.date().isoformat()
    return x


def _next_business_day(d: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(d).normalize() + pd.tseries.offsets.BDay(1)


def _next_available_trading_day(index: pd.DatetimeIndex, after_date: pd.Timestamp) -> Optional[pd.Timestamp]:
    idx = pd.DatetimeIndex(index).sort_values()
    after_date = pd.Timestamp(after_date).normalize()
    future = idx[idx.normalize() > after_date]
    if len(future) == 0:
        return None
    return pd.Timestamp(future[0]).normalize()


def _empty_live_ledger() -> pd.DataFrame:
    cols = [
        "signal_date", "created_at", "updated_at", "data_last_date_at_creation",
        "estimated_trade_date", "actual_trade_date", "status", "v12_signal",
        "v17_signal", "regime", "net_equity_exposure", "target_allocation", "reason",
    ] + [f"weight_{a}" for a in ASSETS]
    return pd.DataFrame(columns=cols)


def _load_live_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        return _empty_live_ledger()
    ledger = pd.read_csv(path)
    for col in ["signal_date", "created_at", "updated_at", "data_last_date_at_creation",
                "estimated_trade_date", "actual_trade_date"]:
        if col in ledger.columns:
            ledger[col] = pd.to_datetime(ledger[col], errors="coerce")
    for col in ["v12_signal", "v17_signal", "net_equity_exposure"] + [f"weight_{a}" for a in ASSETS]:
        if col in ledger.columns:
            ledger[col] = pd.to_numeric(ledger[col], errors="coerce")
    return ledger


def _save_live_ledger(ledger: pd.DataFrame, path: Path) -> None:
    out = ledger.copy()
    for col in ["signal_date", "created_at", "updated_at", "data_last_date_at_creation",
                "estimated_trade_date", "actual_trade_date"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce").dt.strftime("%Y-%m-%d")
    out.to_csv(path, index=False)


def _append_or_update_latest_signal(
    ledger: pd.DataFrame,
    latest_row: pd.Series,
    daily: pd.DataFrame,
) -> Tuple[pd.DataFrame, str]:
    """Append latest signal exactly once, keyed by signal_date."""
    now = pd.Timestamp(datetime.now()).normalize()
    signal_date = pd.Timestamp(latest_row.name).normalize()
    data_last_date = pd.Timestamp(daily.index[daily["SPY"].notna()].max()).normalize()

    actual_trade_date = _next_available_trading_day(daily.index, signal_date)
    estimated_trade_date = actual_trade_date if actual_trade_date is not None else _next_business_day(signal_date)
    status = "ACTIVE" if actual_trade_date is not None and data_last_date >= actual_trade_date else "PENDING_EXECUTION"

    new_row: Dict[str, object] = {
        "signal_date": signal_date,
        "created_at": now,
        "updated_at": now,
        "data_last_date_at_creation": data_last_date,
        "estimated_trade_date": pd.Timestamp(estimated_trade_date).normalize(),
        "actual_trade_date": pd.Timestamp(actual_trade_date).normalize() if actual_trade_date is not None else pd.NaT,
        "status": status,
        "v12_signal": float(latest_row["v12_signal"]),
        "v17_signal": float(latest_row["v17_signal"]),
        "regime": str(latest_row["regime"]),
        "net_equity_exposure": float(latest_row["net_equity_exposure"]),
        "target_allocation": allocation_text(latest_row),
        "reason": str(latest_row["reason"]),
    }
    for asset in ASSETS:
        new_row[f"weight_{asset}"] = float(latest_row.get(f"weight_{asset}", 0.0))

    if ledger.empty:
        return pd.DataFrame([new_row]), "appended_first_signal"

    ledger = ledger.copy()
    ledger["signal_date"] = pd.to_datetime(ledger["signal_date"], errors="coerce").dt.normalize()
    matches = ledger["signal_date"] == signal_date

    if matches.any():
        idx = ledger.index[matches][0]
        original_created = ledger.at[idx, "created_at"] if "created_at" in ledger.columns else new_row["created_at"]
        for k, v in new_row.items():
            if k != "created_at":
                ledger.at[idx, k] = v
        ledger.at[idx, "created_at"] = original_created
        return ledger.sort_values("signal_date").reset_index(drop=True), "updated_existing_signal_no_duplicate"

    max_existing = pd.to_datetime(ledger["signal_date"], errors="coerce").max()
    if pd.notna(max_existing) and signal_date <= pd.Timestamp(max_existing).normalize():
        return ledger.sort_values("signal_date").reset_index(drop=True), "ignored_older_signal"

    ledger = pd.concat([ledger, pd.DataFrame([new_row])], ignore_index=True)
    return ledger.sort_values("signal_date").reset_index(drop=True), "appended_new_signal"


def _refresh_trade_dates_and_status(ledger: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    if ledger.empty:
        return ledger
    ledger = ledger.copy()
    data_last_date = pd.Timestamp(daily.index[daily["SPY"].notna()].max()).normalize()
    for i, row in ledger.iterrows():
        signal_date = pd.Timestamp(row["signal_date"]).normalize()
        actual = _next_available_trading_day(daily.index, signal_date)
        if actual is None:
            ledger.at[i, "actual_trade_date"] = pd.NaT
            if pd.isna(row.get("estimated_trade_date", pd.NaT)):
                ledger.at[i, "estimated_trade_date"] = _next_business_day(signal_date)
            ledger.at[i, "status"] = "PENDING_EXECUTION"
        else:
            actual = pd.Timestamp(actual).normalize()
            ledger.at[i, "actual_trade_date"] = actual
            ledger.at[i, "estimated_trade_date"] = actual
            ledger.at[i, "status"] = "ACTIVE" if data_last_date >= actual else "PENDING_EXECUTION"
    return ledger


def _build_live_weights(ledger: pd.DataFrame, daily_index: pd.DatetimeIndex) -> pd.DataFrame:
    weights = pd.DataFrame(0.0, index=daily_index, columns=ASSETS)
    if ledger.empty:
        return weights

    rows = ledger.dropna(subset=["signal_date"]).copy()
    if rows.empty:
        return weights

    rows["signal_date"] = pd.to_datetime(rows["signal_date"]).dt.normalize()
    rows = rows.sort_values("signal_date")

    signal_w = pd.DataFrame(
        {asset: pd.to_numeric(rows[f"weight_{asset}"], errors="coerce").fillna(0.0).values for asset in ASSETS},
        index=pd.DatetimeIndex(rows["signal_date"]),
    )
    target = signal_w.reindex(daily_index, method="ffill")
    return target.shift(1).fillna(0.0)


def _live_signal_periods(ledger: pd.DataFrame, live_ret: pd.Series, spy_ret: pd.Series) -> pd.DataFrame:
    if ledger.empty:
        return pd.DataFrame()

    rows = ledger.copy()
    rows["signal_date"] = pd.to_datetime(rows["signal_date"], errors="coerce")
    rows["actual_trade_date"] = pd.to_datetime(rows["actual_trade_date"], errors="coerce")
    rows = rows.dropna(subset=["signal_date"]).sort_values("signal_date").reset_index(drop=True)

    out = []
    idx = live_ret.index

    for i, row in rows.iterrows():
        start = row["actual_trade_date"]
        if pd.isna(start):
            out.append({
                "signal_date": row["signal_date"].date().isoformat(),
                "trade_date": "pending",
                "period_end": "pending",
                "status": "PENDING_EXECUTION",
                "regime": row.get("regime", ""),
                "v17_signal": row.get("v17_signal", np.nan),
                "target_allocation": row.get("target_allocation", ""),
                "model_period_return": np.nan,
                "spy_period_return": np.nan,
                "excess_return": np.nan,
            })
            continue

        start = pd.Timestamp(start).normalize()
        if i + 1 < len(rows) and pd.notna(rows.loc[i + 1, "actual_trade_date"]):
            next_start = pd.Timestamp(rows.loc[i + 1, "actual_trade_date"]).normalize()
            period_dates = idx[(idx >= start) & (idx < next_start)]
        else:
            period_dates = idx[idx >= start]

        if len(period_dates) == 0:
            model_r = spy_r = excess = np.nan
            period_end = "pending"
            status = "PENDING_EXECUTION"
        else:
            model_r = float((1.0 + live_ret.loc[period_dates]).prod() - 1.0)
            spy_r = float((1.0 + spy_ret.loc[period_dates]).prod() - 1.0)
            excess = model_r - spy_r
            period_end = pd.Timestamp(period_dates[-1]).date().isoformat()
            status = "CLOSED" if i + 1 < len(rows) and pd.notna(rows.loc[i + 1, "actual_trade_date"]) else "OPEN"

        out.append({
            "signal_date": row["signal_date"].date().isoformat(),
            "trade_date": start.date().isoformat(),
            "period_end": period_end,
            "status": status,
            "regime": row.get("regime", ""),
            "v17_signal": row.get("v17_signal", np.nan),
            "target_allocation": row.get("target_allocation", ""),
            "model_period_return": model_r,
            "spy_period_return": spy_r,
            "excess_return": excess,
        })

    return pd.DataFrame(out)


def update_live_tracker(
    live_dir: Path,
    signal_table: pd.DataFrame,
    daily: pd.DataFrame,
    initial_capital: float,
    reset: bool = False,
) -> Dict[str, object]:
    """Update live paper-tracking files. Safe to rerun multiple times per week."""
    live_dir = Path(live_dir)
    live_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = live_dir / "live_signal_ledger.csv"

    if reset and ledger_path.exists():
        ledger_path.unlink()

    ledger = _load_live_ledger(ledger_path)
    latest_row = signal_table.iloc[-1]

    ledger, action = _append_or_update_latest_signal(ledger, latest_row, daily)
    ledger = _refresh_trade_dates_and_status(ledger, daily)
    _save_live_ledger(ledger, ledger_path)

    first_signal_date = pd.to_datetime(ledger["signal_date"], errors="coerce").dropna().min()
    if pd.isna(first_signal_date):
        return {"action": action, "ledger_path": str(ledger_path), "summary": {}}

    daily_live = daily.loc[pd.Timestamp(first_signal_date):].copy()
    weights = _build_live_weights(ledger, daily_live.index)

    asset_ret = daily_live[ASSETS].ffill().pct_change().fillna(0.0)
    live_ret = (weights * asset_ret).sum(axis=1)
    spy_ret = daily_live["SPY"].ffill().pct_change().fillna(0.0)

    live_equity = initial_capital * (1.0 + live_ret).cumprod()
    spy_equity = initial_capital * (1.0 + spy_ret).cumprod()

    equity_curve = pd.DataFrame({
        "date": daily_live.index,
        "model_equity": live_equity.values,
        "spy_equity": spy_equity.values,
        "model_daily_return": live_ret.values,
        "spy_daily_return": spy_ret.values,
        "excess_daily_return": (live_ret - spy_ret).values,
        "model_drawdown": (live_equity / live_equity.cummax() - 1.0).values,
        "spy_drawdown": (spy_equity / spy_equity.cummax() - 1.0).values,
    })
    for asset in ASSETS:
        equity_curve[f"weight_{asset}"] = weights[asset].values
    equity_curve.to_csv(live_dir / "live_equity_curve.csv", index=False)

    periods = _live_signal_periods(ledger, live_ret, spy_ret)
    periods.to_csv(live_dir / "live_signal_periods.csv", index=False)

    current_weights = weights.tail(1).reset_index(names="date")
    current_weights.to_csv(live_dir / "current_effective_weights.csv", index=False)

    rf_daily = get_rf_daily(daily_live, live_ret.index)

    model_metrics = metrics_daily(live_ret, rf_daily=rf_daily)
    spy_metrics = metrics_daily(spy_ret, rf_daily=rf_daily)

    summary = {
        "initial_capital": float(initial_capital),
        "start_signal_date": pd.Timestamp(first_signal_date).date().isoformat(),
        "last_data_date": pd.Timestamp(daily_live.index.max()).date().isoformat(),
        "latest_signal_date": pd.Timestamp(signal_table.index[-1]).date().isoformat(),
        "latest_tracker_action": action,
        "rows_in_ledger": int(len(ledger)),
        "model_equity": float(live_equity.iloc[-1]) if len(live_equity) else float(initial_capital),
        "spy_equity": float(spy_equity.iloc[-1]) if len(spy_equity) else float(initial_capital),
        "model_total_return": float(model_metrics["total_return"]),
        "spy_total_return": float(spy_metrics["total_return"]),
        "excess_return": float(model_metrics["total_return"] - spy_metrics["total_return"]),
        "model_sharpe": float(model_metrics["sharpe"]) if not pd.isna(model_metrics["sharpe"]) else np.nan,
        "spy_sharpe": float(spy_metrics["sharpe"]) if not pd.isna(spy_metrics["sharpe"]) else np.nan,
        "model_max_drawdown": float(model_metrics["max_drawdown"]),
        "spy_max_drawdown": float(spy_metrics["max_drawdown"]),
        "latest_target_allocation": allocation_text(signal_table.iloc[-1]),
    }

    (live_dir / "live_summary.json").write_text(
        json.dumps({k: _json_safe(v) for k, v in summary.items()}, indent=2),
        encoding="utf-8",
    )
    pd.DataFrame([summary]).to_csv(live_dir / "live_summary.csv", index=False)

    write_live_report(live_dir, ledger, summary, periods)

    return {"action": action, "ledger_path": str(ledger_path), "summary": summary}


def write_live_report(live_dir: Path, ledger: pd.DataFrame, summary: Dict[str, object], periods: pd.DataFrame) -> None:
    lines = []
    lines.append("# V17 Live Paper Tracker")
    lines.append("")
    lines.append(
        "This tracker is duplicate-safe. Rerunning during the same signal week updates reports "
        "but does **not** append a duplicate or fake future Friday signal."
    )
    lines.append("")
    lines.append("## Current summary")
    lines.append("")

    rows = [
        ["Start signal date", summary.get("start_signal_date", "n/a")],
        ["Latest signal date", summary.get("latest_signal_date", "n/a")],
        ["Last data date", summary.get("last_data_date", "n/a")],
        ["Tracker action", summary.get("latest_tracker_action", "n/a")],
        ["Ledger rows", summary.get("rows_in_ledger", "n/a")],
        ["Model equity", f"{summary.get('model_equity', np.nan):,.2f}" if not pd.isna(summary.get("model_equity", np.nan)) else "n/a"],
        ["SPY equity", f"{summary.get('spy_equity', np.nan):,.2f}" if not pd.isna(summary.get("spy_equity", np.nan)) else "n/a"],
        ["Model total return", fmt_pct(summary.get("model_total_return", np.nan))],
        ["SPY total return", fmt_pct(summary.get("spy_total_return", np.nan))],
        ["Excess return", fmt_pct_signed(summary.get("excess_return", np.nan))],
        ["Model Sharpe", fmt_num(summary.get("model_sharpe", np.nan))],
        ["SPY Sharpe", fmt_num(summary.get("spy_sharpe", np.nan))],
        ["Model MaxDD", fmt_pct(summary.get("model_max_drawdown", np.nan))],
        ["SPY MaxDD", fmt_pct(summary.get("spy_max_drawdown", np.nan))],
        ["Latest target allocation", summary.get("latest_target_allocation", "n/a")],
    ]
    lines.append(_markdown_table(["Field", "Value"], rows))
    lines.append("")

    lines.append("## Latest signal ledger rows")
    lines.append("")
    if not ledger.empty:
        show = ledger.tail(8).copy()
        out_rows = []
        for _, r in show.iterrows():
            signal_date = pd.to_datetime(r.get("signal_date"), errors="coerce")
            trade_date = pd.to_datetime(r.get("actual_trade_date"), errors="coerce")
            v17 = pd.to_numeric(pd.Series([r.get("v17_signal", np.nan)]), errors="coerce").iloc[0]
            out_rows.append([
                signal_date.date().isoformat() if pd.notna(signal_date) else "n/a",
                trade_date.date().isoformat() if pd.notna(trade_date) else "pending",
                r.get("status", ""),
                r.get("regime", ""),
                f"{float(v17):.2f}" if pd.notna(v17) else "n/a",
                r.get("target_allocation", ""),
            ])
        lines.append(_markdown_table(["Signal date", "Trade date", "Status", "Regime", "Signal", "Allocation"], out_rows))
    else:
        lines.append("No ledger rows yet.")
    lines.append("")

    lines.append("## Recent signal-period results")
    lines.append("")
    if periods is not None and not periods.empty:
        show = periods.tail(8)
        out_rows = []
        for _, r in show.iterrows():
            out_rows.append([
                r.get("signal_date", ""),
                r.get("trade_date", ""),
                r.get("status", ""),
                r.get("regime", ""),
                fmt_pct_signed(r.get("model_period_return", np.nan)),
                fmt_pct_signed(r.get("spy_period_return", np.nan)),
                fmt_pct_signed(r.get("excess_return", np.nan)),
            ])
        lines.append(_markdown_table(["Signal", "Trade", "Status", "Regime", "Model", "SPY", "Excess"], out_rows))
    else:
        lines.append("No completed/live signal periods yet.")
    lines.append("")

    lines.append("## Files written")
    lines.append("")
    lines.append("- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe")
    lines.append("- `live_equity_curve.csv`: daily model/SPY live-paper equity curve")
    lines.append("- `live_signal_periods.csv`: return attribution by signal period")
    lines.append("- `live_summary.csv` / `live_summary.json`: compact dashboard summary")
    lines.append("- `current_effective_weights.csv`: currently effective tracked weights")
    lines.append("")

    (live_dir / "LIVE_TRACKING_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
