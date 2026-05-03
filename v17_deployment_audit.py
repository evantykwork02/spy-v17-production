"""
SPY V17 Conservative - Deployment Audit

Fast preflight audit for live/paper deployment. It does not change model logic.
It validates data integrity, weekly signal timing, weight/exposure construction,
performance floors, output schemas, and duplicate-safe live tracking.

Typical use:
    py v17_deployment_audit.py --offline
    py v17_deployment_audit.py --refresh-data

Outputs:
    deployment_audit/DEPLOYMENT_AUDIT_REPORT.md
    deployment_audit/deployment_audit_summary.csv
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

import spy_v17_conservative as core
from v17_live_tracker import update_live_tracker

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


def _status(ok: bool, warn: bool = False) -> str:
    if ok:
        return WARN if warn else PASS
    return FAIL


def _fmt(x, pct=False):
    if pd.isna(x):
        return "n/a"
    return f"{x*100:.2f}%" if pct else f"{x:.4f}"


def add(rows: List[Dict[str, str]], category: str, test: str, status: str, detail: str, recommendation: str = "") -> None:
    rows.append({
        "category": category,
        "test": test,
        "status": status,
        "detail": detail,
        "recommendation": recommendation,
    })


def audit_data(daily: pd.DataFrame, rows: List[Dict[str, str]]) -> None:
    required = core.ASSETS + ["VIX", "VIX3M"]
    missing = [c for c in required if c not in daily.columns]
    add(rows, "data", "required columns present", _status(len(missing) == 0),
        f"missing={missing}" if missing else f"all required columns present: {', '.join(required)}")

    add(rows, "data", "date index monotonic", _status(daily.index.is_monotonic_increasing),
        f"rows={len(daily)}, start={daily.index.min().date()}, end={daily.index.max().date()}")
    dupes = int(pd.Index(daily.index).duplicated().sum())
    add(rows, "data", "duplicate dates", _status(dupes == 0), f"duplicate_dates={dupes}")

    nonpositive = []
    for c in core.ASSETS:
        if c in daily.columns and (daily[c].dropna() <= 0).any():
            nonpositive.append(c)
    add(rows, "data", "positive asset prices", _status(len(nonpositive) == 0),
        f"nonpositive_columns={nonpositive}" if nonpositive else "all asset prices are positive")

    spy_ret = daily["SPY"].pct_change().dropna() if "SPY" in daily.columns else pd.Series(dtype=float)
    max_abs = float(spy_ret.abs().max()) if len(spy_ret) else np.nan
    add(rows, "data", "SPY daily outlier guard", _status(pd.notna(max_abs) and max_abs < 0.30),
        f"max_abs_daily_return={_fmt(max_abs, pct=True)}", "Investigate source prices if >30%.")

    na_counts = daily[core.ASSETS].isna().sum().to_dict()
    add(rows, "data", "asset missing values after aligned start", _status(sum(na_counts.values()) == 0),
        f"missing_counts={na_counts}", "Cache should be aligned to first valid date across all tradeable assets.")

    age_days = (pd.Timestamp(datetime.now()).normalize() - pd.Timestamp(daily.index.max()).normalize()).days
    stale_status = PASS if age_days <= 4 else WARN if age_days <= 8 else FAIL
    add(rows, "data", "data freshness", stale_status,
        f"last_data_date={pd.Timestamp(daily.index.max()).date()}, age_calendar_days={age_days}",
        "For a real weekly run, use --refresh-data after the latest Friday close.")


def audit_timing(daily: pd.DataFrame, weekly: pd.DataFrame, signal: pd.Series, rows: List[Dict[str, str]]) -> None:
    # Partial current week guard: Wednesday data must not create a future Friday signal.
    weds = [d for d in daily.index if pd.Timestamp(d).weekday() == 2]
    if weds:
        midweek = pd.Timestamp(weds[-1]).normalize()
        partial = daily.loc[:midweek]
        weekly_partial = core.resample_completed_friday_weeks(partial, as_of=midweek)
        ok = weekly_partial.empty or pd.Timestamp(weekly_partial.index.max()).normalize() <= midweek
        add(rows, "timing", "no fake future Friday on midweek rerun", _status(ok),
            f"simulated_as_of={midweek.date()}, last_weekly_label={weekly_partial.index.max().date() if len(weekly_partial) else 'none'}")

    bt = core.run_backtest(signal, daily, tc_bps=5.0)
    weekly_w = core.signal_to_weekly_weights(signal, weekly)
    daily_w = bt["weights"]
    changed = weekly_w.diff().abs().sum(axis=1) > 1e-12
    failures = []
    for dt in weekly_w.index[changed].tolist()[1:]:
        dt = pd.Timestamp(dt)
        if dt not in daily_w.index:
            continue
        loc = daily_w.index.get_loc(dt)
        if isinstance(loc, slice) or loc == 0 or loc + 1 >= len(daily_w.index):
            continue
        prev_target = weekly_w.loc[:dt].iloc[-2]
        new_target = weekly_w.loc[dt]
        next_day = daily_w.index[loc + 1]
        friday_uses_prev = np.allclose(daily_w.loc[dt, core.ASSETS].values, prev_target[core.ASSETS].values, atol=1e-12)
        next_uses_new = np.allclose(daily_w.loc[next_day, core.ASSETS].values, new_target[core.ASSETS].values, atol=1e-12)
        if not (friday_uses_prev and next_uses_new):
            failures.append(str(dt.date()))
            if len(failures) >= 5:
                break
    add(rows, "timing", "Friday signal delayed by one daily bar", _status(len(failures) == 0),
        f"changed_weeks_checked={int(changed.sum())}, failures={failures}",
        "Backtest uses next trading day's close-to-close return as a proxy; live Monday-open execution can differ from this proxy.")


def audit_weights_and_performance(daily: pd.DataFrame, weekly: pd.DataFrame, v12: pd.Series, v17: pd.Series, rows: List[Dict[str, str]]) -> Dict[str, Dict]:
    bt = {
        "SPY_BH": {"ret": daily["SPY"].ffill().pct_change().fillna(0.0), "exposure": pd.Series(1.0, index=daily.index)},
        "v12": core.run_backtest(v12, daily, 5.0),
        "v17_conservative": core.run_backtest(v17, daily, 5.0),
    }
    w = bt["v17_conservative"]["weights"]
    row_sum = w[core.ASSETS].sum(axis=1)
    min_w = float(w[core.ASSETS].min().min())
    max_w = float(w[core.ASSETS].max().max())
    exposure = bt["v17_conservative"]["exposure"]
    ok_weights = min_w >= -1e-12 and max_w <= 1.0 + 1e-12 and np.allclose(row_sum, 1.0, atol=1e-10)
    add(rows, "weights", "weights sum and bounds", _status(ok_weights),
        f"min_weight={min_w:.6f}, max_weight={max_w:.6f}, min_sum={row_sum.min():.6f}, max_sum={row_sum.max():.6f}")
    ok_exposure = exposure.min() >= -1.000001 and exposure.max() <= 1.800001
    add(rows, "weights", "net exposure bounds", _status(ok_exposure),
        f"min_exposure={exposure.min():.2f}, max_exposure={exposure.max():.2f}, avg_exposure={exposure.mean():.2f}")

    headline = core.headline_comparison(bt, daily)
    full_spy = headline[(headline.period == "full") & (headline.model == "SPY_BH")].iloc[0]
    full_v17 = headline[(headline.period == "full") & (headline.model == "v17_conservative")].iloc[0]
    hold_spy = headline[(headline.period == "holdout_2021_plus") & (headline.model == "SPY_BH")].iloc[0]
    hold_v17 = headline[(headline.period == "holdout_2021_plus") & (headline.model == "v17_conservative")].iloc[0]

    add(rows, "performance", "full-period CAGR > SPY", _status(full_v17.cagr > full_spy.cagr),
        f"V17={_fmt(full_v17.cagr, pct=True)}, SPY={_fmt(full_spy.cagr, pct=True)}")
    add(rows, "performance", "full-period Sharpe > SPY", _status(full_v17.sharpe > full_spy.sharpe),
        f"V17={full_v17.sharpe:.3f}, SPY={full_spy.sharpe:.3f}")
    add(rows, "performance", "full-period max drawdown better than SPY", _status(full_v17.max_drawdown > full_spy.max_drawdown),
        f"V17={_fmt(full_v17.max_drawdown, pct=True)}, SPY={_fmt(full_spy.max_drawdown, pct=True)}")
    add(rows, "performance", "holdout Sharpe > SPY", _status(hold_v17.sharpe > hold_spy.sharpe),
        f"V17={hold_v17.sharpe:.3f}, SPY={hold_spy.sharpe:.3f}")
    add(rows, "performance", "holdout max drawdown better than SPY", _status(hold_v17.max_drawdown > hold_spy.max_drawdown),
        f"V17={_fmt(hold_v17.max_drawdown, pct=True)}, SPY={_fmt(hold_spy.max_drawdown, pct=True)}")
    return bt


def audit_live_tracker(signal_table: pd.DataFrame, daily: pd.DataFrame, out: Path, rows: List[Dict[str, str]]) -> None:
    live_dir = out / "_tmp_live_tracker_duplicate_test"
    if live_dir.exists():
        shutil.rmtree(live_dir)
    r1 = update_live_tracker(live_dir, signal_table, daily, initial_capital=10000.0, reset=True)
    r2 = update_live_tracker(live_dir, signal_table, daily, initial_capital=10000.0, reset=False)
    ledger = pd.read_csv(live_dir / "live_signal_ledger.csv")
    ok = (len(ledger) == 1) and (r2.get("action") == "updated_existing_signal_no_duplicate")
    add(rows, "live_tracker", "duplicate-safe same-signal rerun", _status(ok),
        f"first_action={r1.get('action')}, second_action={r2.get('action')}, ledger_rows={len(ledger)}")


def write_report(out: Path, rows: List[Dict[str, str]], latest: pd.Series, data_source: str) -> None:
    df = pd.DataFrame(rows)
    df.to_csv(out / "deployment_audit_summary.csv", index=False)
    counts = df["status"].value_counts().to_dict()
    overall = FAIL if counts.get(FAIL, 0) else WARN if counts.get(WARN, 0) else PASS
    lines = []
    lines.append("# SPY V17 Conservative - Deployment Audit Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Overall status: **{overall}**")
    lines.append(f"Counts: PASS={counts.get(PASS,0)}, WARN={counts.get(WARN,0)}, FAIL={counts.get(FAIL,0)}")
    lines.append("")
    lines.append("## Latest signal")
    lines.append("")
    lines.append(f"- Signal date: {pd.Timestamp(latest.name).date()}")
    lines.append(f"- Regime: {latest['regime']}")
    lines.append(f"- V17 signal / net exposure: {float(latest['v17_signal']):.2f}x")
    lines.append(f"- Allocation: {core.allocation_text(latest)}")
    lines.append(f"- Reason: {latest['reason']}")
    lines.append(f"- Data source: {data_source}")
    lines.append("")
    lines.append("## Audit checks")
    lines.append("")
    lines.append("| Category | Test | Status | Detail | Recommendation |")
    lines.append("|---|---:|:---:|---|---|")
    for _, r in df.iterrows():
        detail = str(r.detail).replace("|", "\\|")
        rec = str(r.recommendation).replace("|", "\\|")
        lines.append(f"| {r.category} | {r.test} | {r.status} | {detail} | {rec} |")
    lines.append("")
    lines.append("## Deployment note")
    lines.append("")
    lines.append("This audit validates mechanics and historical robustness. It does not guarantee future profit. For live testing, keep the model logic frozen, use the refreshed Friday-after-close signal, record actual fills, and compare live returns against the tracker and SPY.")
    (out / "DEPLOYMENT_AUDIT_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parent
    out = root / args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    daily, data_source = core.fetch_and_clean_data(root / "data" / "daily_cache.parquet", refresh=args.refresh_data, offline=args.offline)
    weekly = core.resample_completed_friday_weeks(daily)
    v12 = core.strat_v12_robust_short_ensemble(weekly)
    v17, diagnostics = core.build_v17_conservative_signal(weekly, v12)
    signal_table = core.build_signal_table(v12, v17, diagnostics, weekly)

    rows: List[Dict[str, str]] = []
    audit_data(daily, rows)
    audit_timing(daily, weekly, v17, rows)
    audit_weights_and_performance(daily, weekly, v12, v17, rows)
    audit_live_tracker(signal_table, daily, out, rows)
    write_report(out, rows, signal_table.iloc[-1], data_source)

    df = pd.DataFrame(rows)
    fail = int((df.status == FAIL).sum())
    warn = int((df.status == WARN).sum())
    print(f"Deployment audit complete: PASS={(df.status == PASS).sum()}, WARN={warn}, FAIL={fail}")
    print(f"Report: {out / 'DEPLOYMENT_AUDIT_REPORT.md'}")
    return 2 if fail else 1 if warn else 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fast deployment audit for SPY V17 Conservative.")
    p.add_argument("--offline", action="store_true", help="Use cached data only.")
    p.add_argument("--refresh-data", action="store_true", help="Refresh market data before auditing.")
    p.add_argument("--out-dir", default="deployment_audit")
    return p.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
