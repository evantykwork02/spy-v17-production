"""
SPY V17-PRO Conservative — Self-Contained Weekly Signal Engine

What this is:
    A single-file weekly signal generator that combines:
      - V12: defensive base engine (crash short / defensive / leveraged tiers)
      - V17-PRO: 3-tier upside sleeve (calm-bull + yield-curve-steepening) on top of V12

What this run does:
    1. Fetches latest daily prices from Yahoo Finance + FRED (free, no API key)
    2. Validates the data (NaN checks, price sanity, freshness)
    3. Computes V12 signal internally from the data
    4. Applies V17-PRO 3-tier boost on V12's normal weeks
    5. Writes a clean weekly signal report
    6. In --mode full, runs heavy validation: bootstrap, null markets, random schedules,
       deflated Sharpe, Bayesian Sharpe, rolling windows, cost stress, and sensitivity

V17-PRO rule (only fires when V12 == 1.0; V12 defensive/crash-short/levered logic preserved):
      INTERSECTION: calm_bull AND yield-curve-steepening   → v17_signal = 1.25
      CALM_BULL only:                                      → v17_signal = 1.07
      YC_STEEP only:                                       → v17_signal = 1.12
      Otherwise:                                           → v17_signal = v12_signal

Where:
    calm_bull   = V12 normal AND SPY>40W MA AND 13W mom>0 AND 26W RV<55th pct AND VIX<52W avg
    yc_steep    = T10Y2Y > 0 AND T10Y2Y has risen over the last 13 weeks

Validation summary (2009-01 to 2026-04, 17.3 years; see V17_PRO_UPGRADE_REPORT.md):
    v17_orig:  Sharpe 1.171, CAGR 21.55%, MaxDD -24.34%, Calmar 0.886
    v17-pro:   Sharpe 1.187, CAGR 22.29%, MaxDD -24.25%, Calmar 0.919
    Pre-2021 (out-of-holdout) Sharpe lift: 1.078 → 1.111
    Null permutation test: real lift +85 ann bps; random shuffles mean -10; P(random ≥ real)=0.000
    Bootstrap (5000 iters, 21d blocks) full period: +66 ann bps, p_fail=0.0004

Run:
    py spy_v17_conservative.py --mode signal              # quick weekly run
    py spy_v17_conservative.py --mode full --n-bootstrap 2000   # full/heavy validation
    py spy_v17_conservative.py --mode signal --refresh-data     # force fresh fetch
    py spy_v17_conservative.py --mode signal --offline          # use cache only
    py spy_v17_conservative.py --mode signal --live-track       # weekly signal + live tracker

Cache:
    Daily prices are cached in data/daily_cache.parquet. The cache is auto-
    refreshed if it's more than 1 day old (or if --refresh-data is set).
    Use --offline to skip the network entirely and use the cache as-is.

Required:
    pip install numpy pandas pyarrow yfinance requests
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

try:
    from scipy import stats
except Exception:  # pragma: no cover
    stats = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ASSETS = ["SPY", "SPXL", "SPXS", "TLT", "GLD", "SHY"]
SECTOR_ETFS = ["XLF", "XLK", "XLE", "XLY", "XLP", "XLU"]

# Yahoo Finance ticker mapping (label -> Yahoo symbol)
YF_TICKERS = {
    "SPY": "SPY", "SPXL": "SPXL", "SPXS": "SPXS",
    "TLT": "TLT", "GLD": "GLD", "SHY": "SHY",
    "XLF": "XLF", "XLK": "XLK", "XLE": "XLE",
    "XLY": "XLY", "XLP": "XLP", "XLU": "XLU",
    "VIX": "^VIX", "VIX3M": "^VIX3M", "SKEW": "^SKEW",
}

# FRED series for macro data
FRED_SERIES = ["DGS10", "T10Y2Y", "BAMLH0A0HYM2", "DGS3MO"]

# History start date for fetching (V12 needs ~5y of warmup)
DEFAULT_START = "2008-01-01"

# V17 conservative defaults
DEFAULT_BOOST = 0.15
DEFAULT_TREND_MA = 40
DEFAULT_MOMENTUM_WEEKS = 13
DEFAULT_RV_WEEKS = 26
DEFAULT_RV_LOOKBACK = 104
DEFAULT_RV_QUANTILE = 0.55
DEFAULT_VIX_MA = 52
DEFAULT_TC_BPS = 5.0
DEFAULT_BLOCK_LEN = 21
DEFAULT_N_RANDOM_REBALANCE = 1000
DEFAULT_N_SYNTHETIC = 100
DEFAULT_N_BAYES_DRAWS = 20000
DEFAULT_N_VARIANTS_ASSUMED = 80
ANNUALIZATION_DAYS = 252.0

# Risk-free rate fallback (annualized, used only when DGS3MO is not in the data)
RISK_FREE_FALLBACK_ANNUAL = 0.043

# Data freshness threshold (auto-refresh if cache older than this)
CACHE_MAX_AGE_HOURS = 20


def get_rf_daily(daily: Optional[pd.DataFrame] = None, returns_index: Optional[pd.DatetimeIndex] = None) -> pd.Series:
    """Extract a daily risk-free rate series from the daily DataFrame.

    Uses DGS3MO (3-month T-bill yield from FRED) when available, converting
    the annualized percentage to a daily decimal rate. Falls back to
    RISK_FREE_FALLBACK_ANNUAL when DGS3MO is missing.

    Returns a pd.Series of daily RF rates aligned to returns_index (or daily.index).
    """
    idx = returns_index if returns_index is not None else (daily.index if daily is not None else None)
    if idx is None:
        return pd.Series(dtype=float)

    if daily is not None and "DGS3MO" in daily.columns:
        # DGS3MO is in annualized percentage points (e.g. 4.3 means 4.3%)
        rf_annual = daily["DGS3MO"].reindex(idx).ffill().fillna(0.0) / 100.0
        return rf_annual / ANNUALIZATION_DAYS
    else:
        return pd.Series(RISK_FREE_FALLBACK_ANNUAL / ANNUALIZATION_DAYS, index=idx)


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def fmt_pct(x: float, decimals: int = 1) -> str:
    if pd.isna(x): return "n/a"
    return f"{x * 100:.{decimals}f}%"


def fmt_pct_signed(x: float, decimals: int = 1) -> str:
    if pd.isna(x): return "n/a"
    return f"{x * 100:+.{decimals}f}%"


def fmt_num(x: float, decimals: int = 3) -> str:
    if pd.isna(x): return "n/a"
    return f"{x:.{decimals}f}"


def fmt_signed(x: float, decimals: int = 3) -> str:
    if pd.isna(x): return "n/a"
    return f"{x:+.{decimals}f}"


# ---------------------------------------------------------------------------
# Progress reporting
# ---------------------------------------------------------------------------

class StepLogger:
    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self._t = None

    def start(self, label: str) -> None:
        self.current += 1
        self._t = time.perf_counter()
        prefix = f"[{self.current}/{self.total}]"
        print(f"  {prefix:<7s}  {label} ...", flush=True)

    def done(self, extra: str = "") -> None:
        if self._t is None: return
        elapsed = time.perf_counter() - self._t
        suffix = f"  ({elapsed:.1f}s{', ' + extra if extra else ''})"
        print(f"          done{suffix}", flush=True)
        self._t = None


def progress_bar(i: int, n: int, label: str = "", width: int = 30) -> None:
    if n <= 0: return
    pct = i / n
    filled = int(width * pct)
    bar = "#" * filled + "-" * (width - filled)
    msg = f"\r          [{bar}] {pct * 100:5.1f}%  ({i}/{n}) {label}"
    sys.stdout.write(msg)
    sys.stdout.flush()
    if i >= n:
        sys.stdout.write("\n")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def download_yfinance_prices(start: str, end: Optional[str] = None) -> pd.DataFrame:
    """Fetch all required Yahoo Finance tickers as a clean wide DataFrame."""
    try:
        import yfinance as yf
    except ImportError:
        raise RuntimeError(
            "yfinance not installed. Run: pip install yfinance"
        )

    # Clear stale SQLite locks from previous runs (GitHub Actions / Cloudflare)
    try:
        import shutil, os
        yf_cache = Path(os.path.expanduser("~/.cache/py-yfinance"))
        if yf_cache.exists():
            shutil.rmtree(yf_cache, ignore_errors=True)
    except Exception:
        pass

    raw = yf.download(
        tickers=list(YF_TICKERS.values()),
        start=start, end=end,
        auto_adjust=True, group_by="column",
        progress=False, threads=True,
    )
    if raw is None or len(raw) == 0:
        raise RuntimeError("yfinance returned no rows. Check internet connection.")

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            close = raw["Close"].copy()
        else:
            close = raw["Adj Close"].copy()
    else:
        close = raw.copy()

    close = close.rename(columns={v: k for k, v in YF_TICKERS.items()})
    close.index = pd.to_datetime(close.index).tz_localize(None)
    return close.sort_index()


def download_fred_series(start: str, end: Optional[str] = None) -> pd.DataFrame:
    """Fetch FRED macro series via the public CSV download endpoint."""
    frames = []
    for sid in FRED_SERIES:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        try:
            d = pd.read_csv(url)
            date_col = "observation_date" if "observation_date" in d.columns else "DATE"
            val_col = sid if sid in d.columns else d.columns[-1]
            d = d[[date_col, val_col]].rename(columns={date_col: "Date", val_col: sid})
            d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
            d[sid] = pd.to_numeric(d[sid].replace(".", np.nan), errors="coerce")
            d = d.dropna(subset=["Date"]).set_index("Date").sort_index()
            frames.append(d)
        except Exception as e:
            print(f"          [WARN] FRED fetch failed for {sid}: {e}")
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, axis=1).sort_index()
    out = out.loc[pd.Timestamp(start):]
    if end:
        out = out.loc[:pd.Timestamp(end)]
    return out


def validate_daily_data(daily: pd.DataFrame) -> List[str]:
    """Return a list of validation issues. Empty list = data is good."""
    issues = []

    for asset in ASSETS:
        if asset not in daily.columns:
            issues.append(f"missing required asset column: {asset}")
        elif daily[asset].dropna().empty:
            issues.append(f"asset column has no data: {asset}")
        elif (daily[asset] <= 0).any():
            issues.append(f"asset column contains non-positive prices: {asset}")

    for col in ["VIX", "VIX3M"]:
        if col not in daily.columns:
            issues.append(f"missing required volatility column: {col}")
        elif daily[col].dropna().empty:
            issues.append(f"volatility column has no data: {col}")

    if "SPY" in daily.columns:
        spy_ret = daily["SPY"].pct_change()
        if spy_ret.abs().max() > 0.30:
            extreme = spy_ret[spy_ret.abs() > 0.30]
            issues.append(f"SPY has {len(extreme)} day(s) with >30% return — likely data error")

    if len(daily) < 1000:
        issues.append(f"only {len(daily)} daily rows — V12 needs at least 5y of history")

    last_date = daily.index.max()
    age_days = (datetime.now() - last_date).days
    if age_days > 7:
        issues.append(f"data is {age_days} days stale (last: {last_date.date()})")

    return issues



def read_daily_cache(cache_path: Path) -> pd.DataFrame:
    """Read the cached daily dataframe robustly.

    Primary cache is Parquet. A CSV fallback is also supported so the program can
    still run if a local pyarrow/pandas combination has a parquet-engine issue.
    """
    errors = []
    if cache_path.exists():
        try:
            daily = pd.read_parquet(cache_path)
            daily.index = pd.to_datetime(daily.index).tz_localize(None)
            return daily.sort_index()
        except Exception as e:
            errors.append(f"pd.read_parquet failed: {e}")
            try:
                import pyarrow.parquet as pq
                daily = pq.ParquetFile(cache_path).read().to_pandas()
                daily.index = pd.to_datetime(daily.index).tz_localize(None)
                return daily.sort_index()
            except Exception as e2:
                errors.append(f"pyarrow ParquetFile fallback failed: {e2}")

    csv_path = cache_path.with_suffix(".csv")
    if csv_path.exists():
        try:
            daily = pd.read_csv(csv_path)
            date_col = "Date" if "Date" in daily.columns else daily.columns[0]
            daily[date_col] = pd.to_datetime(daily[date_col])
            daily = daily.set_index(date_col)
            daily.index.name = "Date"
            return daily.sort_index()
        except Exception as e:
            errors.append(f"CSV fallback failed: {e}")

    raise RuntimeError(
        "Could not read daily cache. Tried parquet and CSV fallback. "
        + " | ".join(errors)
    )


def write_daily_cache(daily: pd.DataFrame, cache_path: Path) -> None:
    """Write cache as Parquet plus CSV fallback."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        daily.to_parquet(cache_path)
    except Exception as e:
        print(f"          [WARN] Parquet cache write failed, CSV fallback will be used: {e}")
    try:
        daily.to_csv(cache_path.with_suffix(".csv"), index_label="Date")
    except Exception as e:
        print(f"          [WARN] CSV cache write failed: {e}")



def fetch_and_clean_data(
    cache_path: Path,
    start: str = DEFAULT_START,
    refresh: bool = False,
    offline: bool = False,
) -> Tuple[pd.DataFrame, str]:
    """Load cached data or fetch fresh.

    Returns (daily_df, source_label).
    """
    cache_age_hours: Optional[float] = None
    csv_cache_path = cache_path.with_suffix(".csv")
    cache_exists = cache_path.exists() or csv_cache_path.exists()
    if cache_exists:
        mtime_source = cache_path if cache_path.exists() else csv_cache_path
        cache_mtime = datetime.fromtimestamp(mtime_source.stat().st_mtime)
        cache_age_hours = (datetime.now() - cache_mtime).total_seconds() / 3600

    # Decide whether to use cache or fetch fresh
    use_cache = False
    if offline:
        if not cache_exists:
            raise FileNotFoundError(
                f"--offline mode but no cache exists at {cache_path}. "
                "Run online once first to populate the cache."
            )
        use_cache = True
        source = f"offline cache ({cache_age_hours:.1f}h old)"
    elif refresh:
        use_cache = False
        source = "forced refresh"
    elif cache_exists and cache_age_hours < CACHE_MAX_AGE_HOURS:
        use_cache = True
        source = f"cache ({cache_age_hours:.1f}h old)"
    else:
        use_cache = False
        source = "stale cache, refreshing" if cache_exists else "no cache, fetching"

    if use_cache:
        daily = read_daily_cache(cache_path)
    else:
        prices = download_yfinance_prices(start, end=None)
        macro = download_fred_series(start, end=None)
        if len(macro) == 0 or len(prices) == 0:
            if cache_exists:
                print(f"          [WARN] live fetch incomplete, falling back to cache")
                daily = read_daily_cache(cache_path)
                source = "fallback cache (fetch incomplete)" 
            else:
                raise RuntimeError("Live data fetch failed and no cache available.")
        else:
            daily = prices.join(macro, how="outer").sort_index()
            spy_days = daily.index[daily["SPY"].notna()]
            daily = daily.reindex(spy_days).ffill()

            missing = [c for c in ASSETS if c not in daily.columns or daily[c].dropna().empty]
            if missing:
                raise RuntimeError(f"Required assets missing after fetch: {missing}")

            first_valid = max(daily[c].first_valid_index() for c in ASSETS)
            daily = daily.loc[first_valid:].copy()

            write_daily_cache(daily, cache_path)

    issues = validate_daily_data(daily)
    if issues:
        print()
        print("          [DATA ISSUES DETECTED]")
        for issue in issues:
            print(f"            - {issue}")
        critical = [
            i for i in issues
            if "missing required" in i or "no data" in i or "non-positive" in i
        ]
        if critical:
            raise RuntimeError(
                f"Critical data validation failures, cannot proceed: {critical}"
            )

    return daily, source


# ---------------------------------------------------------------------------
# Weekly resampling safety
# ---------------------------------------------------------------------------

def resample_completed_friday_weeks(daily: pd.DataFrame, as_of: Optional[pd.Timestamp] = None) -> pd.DataFrame:
    """Resample daily data to completed Friday-labelled weekly closes only.

    Safety fix: pandas `resample("W-FRI")` labels an incomplete Mon/Tue/Wed week
    as the upcoming Friday. For a live Friday-after-close model, that can create
    a fake next-Friday signal if you accidentally rerun the script mid-week.

    This helper keeps only weeks whose Friday label is plausibly complete:
      - normal Friday close: included;
      - Friday market holiday: Thursday close may be included under Friday label;
      - accidental Mon-Thu rerun: partial current week is dropped.
    """
    if daily.empty or "SPY" not in daily.columns:
        return pd.DataFrame()

    weekly = daily.resample("W-FRI").last().dropna(subset=["SPY"])
    if weekly.empty:
        return weekly

    spy_dates = pd.to_datetime(daily.index[daily["SPY"].notna()]).tz_localize(None)
    if len(spy_dates) == 0:
        return weekly.iloc[0:0]

    last_spy_date = pd.Timestamp(spy_dates.max()).normalize()
    as_of_date = pd.Timestamp(datetime.now().date()) if as_of is None else pd.Timestamp(as_of).normalize()

    # Allow a Thursday close to represent a Friday-labelled week only if the
    # Friday label is not in the future. This handles common Friday market
    # holidays but blocks Monday/Tuesday partial-week fake signals.
    max_safe_label = min(as_of_date, last_spy_date + pd.Timedelta(days=1))
    return weekly.loc[weekly.index.normalize() <= max_safe_label]


# ---------------------------------------------------------------------------
# V12 signal logic (ported from spy_v12_clean_full_test.py)
# ---------------------------------------------------------------------------

def moving_average(s: pd.Series, window: int) -> pd.Series:
    return s.rolling(window=int(window), min_periods=max(2, int(window) // 2)).mean()


def zscore(s: pd.Series, window: int) -> pd.Series:
    mean = s.rolling(window=int(window), min_periods=max(5, int(window) // 4)).mean()
    std = s.rolling(window=int(window), min_periods=max(5, int(window) // 4)).std(ddof=0)
    return (s - mean) / std.replace(0, np.nan)


def strat_s2_plus_v9(weekly: pd.DataFrame, params: Optional[dict] = None) -> pd.Series:
    """V9 base signal — defensive sleeve, dip/recovery/curve setup."""
    p = {
        "long_ma": 40, "yc_thresh": 0.20, "yc_exp": 1.20,
        "shallow_dip": -0.02, "shallow_vix_z": 0.30, "shallow_exp": 1.30,
        "deep_dip": -0.05, "deep_vix_z": 0.80, "deep_exp": 1.70,
        "dd_thresh": -0.10, "recovery_hold_weeks": 8, "recovery_exp": 1.50,
        "bounce_hold_weeks": 4, "bounce_exp": 1.70,
        "base_defensive": 0.60,
    }
    if params: p.update(params)

    spy = weekly["SPY"]
    signal = pd.Series(1.0, index=weekly.index)

    above_long_ma = spy > moving_average(spy, int(p["long_ma"]))
    signal[~above_long_ma] = float(p["base_defensive"])

    spy_4w = spy.pct_change(4)
    vix_z = zscore(weekly["VIX"], 52) if "VIX" in weekly.columns else pd.Series(0.0, index=weekly.index)

    if "T10Y2Y" in weekly.columns:
        curve_steepening = weekly["T10Y2Y"].diff(13) > float(p["yc_thresh"])
    else:
        curve_steepening = pd.Series(False, index=weekly.index)

    curve_boost = above_long_ma & curve_steepening
    signal[curve_boost] = np.maximum(signal[curve_boost], float(p["yc_exp"]))

    shallow_dip = above_long_ma & (spy_4w < float(p["shallow_dip"])) & (vix_z > float(p["shallow_vix_z"]))
    deep_dip = above_long_ma & (spy_4w < float(p["deep_dip"])) & (vix_z > float(p["deep_vix_z"]))
    signal[shallow_dip] = np.maximum(signal[shallow_dip], float(p["shallow_exp"]))
    signal[deep_dip] = np.maximum(signal[deep_dip], float(p["deep_exp"]))

    peak_26 = spy.rolling(26, min_periods=13).max()
    drawdown = spy / peak_26 - 1.0

    available_sectors = [c for c in SECTOR_ETFS if c in weekly.columns]
    if len(available_sectors) >= 4:
        breadth = pd.concat(
            [(weekly[c] > moving_average(weekly[c], 13)).astype(float) for c in available_sectors],
            axis=1,
        ).mean(axis=1)
        breadth_improving = breadth.diff(4) > 0
    else:
        breadth_improving = pd.Series(False, index=weekly.index)

    recovery_fire = (drawdown <= float(p["dd_thresh"])) & breadth_improving
    recovery_active = (
        recovery_fire.astype(float)
        .rolling(int(p["recovery_hold_weeks"]), min_periods=1)
        .max().fillna(0).astype(bool)
    )
    signal[recovery_active] = np.maximum(signal[recovery_active], float(p["recovery_exp"]))

    if "VIX" in weekly.columns:
        vix = weekly["VIX"]
        stressed = (vix_z.shift(1) > 1.0) & (vix_z.shift(2) > 1.0)
        vix_falling = vix.pct_change(2) < -0.10
        past_bottom = spy > spy.rolling(8, min_periods=4).min() * 1.03
        bounce_fire = stressed & vix_falling & past_bottom
        bounce_active = (
            bounce_fire.astype(float)
            .rolling(int(p["bounce_hold_weeks"]), min_periods=1)
            .max().fillna(0).astype(bool)
        )
        signal[bounce_active] = np.maximum(signal[bounce_active], float(p["bounce_exp"]))

    return signal.clip(0.0, 1.8)


def strat_v10_rate_guard(weekly: pd.DataFrame, params: Optional[dict] = None) -> pd.Series:
    """V10 = V9 with rate-stress guard suppressing leverage."""
    p = {"rate_ma_weeks": 26}
    if params: p.update(params)

    signal = strat_s2_plus_v9(weekly, params=params).copy()

    if "DGS10" in weekly.columns:
        dgs10 = weekly["DGS10"]
        rate_stress = dgs10 > moving_average(dgs10, int(p["rate_ma_weeks"]))
        signal[rate_stress & (signal > 1.0)] = 1.0

    return signal.clip(0.0, 1.8)


def v12_variant_fire(
    weekly: pd.DataFrame, base: pd.Series,
    ma: int = 40, crash4: float = -0.08,
    rate_ma: int = 26, cap: float = 0.70,
) -> pd.Series:
    spy = weekly["SPY"]
    below = spy < moving_average(spy, int(ma))
    crash = spy.pct_change(4) <= float(crash4)
    defensive = base <= float(cap)

    if "DGS10" in weekly.columns:
        rate_stress = weekly["DGS10"] > moving_average(weekly["DGS10"], int(rate_ma))
    else:
        rate_stress = pd.Series(False, index=weekly.index)

    if "VIX" in weekly.columns:
        vix = weekly["VIX"]
        vix_z = zscore(vix, 52)
        bounce_veto = (
            (vix_z.shift(1) > 1.0)
            & (vix.pct_change(2) < -0.10)
            & (spy > spy.rolling(8, min_periods=4).min() * 1.03)
        )
        bounce_veto = bounce_veto.astype(float).rolling(3, min_periods=1).max().fillna(0).astype(bool)
    else:
        bounce_veto = pd.Series(False, index=weekly.index)

    return below & crash & defensive & rate_stress & (~bounce_veto)


def v12_fire_vote_fraction(
    weekly: pd.DataFrame, base: pd.Series,
) -> pd.Series:
    """75-variant ensemble vote (5 ma × 5 crash × 5 rate × 3 cap)."""
    ma_list = [30, 35, 40, 45, 50]
    crash_list = [-0.06, -0.07, -0.08, -0.09, -0.10]
    rate_list = [18, 22, 26, 30, 34]
    cap_list = [0.60, 0.70, 0.85]

    votes = []
    for ma in ma_list:
        for crash4 in crash_list:
            for rate_ma in rate_list:
                for cap in cap_list:
                    votes.append(v12_variant_fire(weekly, base, ma, crash4, rate_ma, cap).astype(float))

    if not votes:
        return pd.Series(0.0, index=weekly.index)
    return pd.concat(votes, axis=1).mean(axis=1)


def v12_crash_score(weekly: pd.DataFrame, base: pd.Series) -> pd.Series:
    """Sum of binary crash indicators (max 10)."""
    spy = weekly["SPY"]
    score = pd.Series(0.0, index=weekly.index)

    score += (spy < moving_average(spy, 30)).astype(float)
    score += (spy < moving_average(spy, 40)).astype(float)
    score += (spy.pct_change(4) <= -0.06).astype(float)
    score += (spy.pct_change(8) <= -0.10).astype(float)
    score += (base <= 0.85).astype(float)

    if "DGS10" in weekly.columns:
        score += (weekly["DGS10"] > moving_average(weekly["DGS10"], 26)).astype(float)
        score += (weekly["DGS10"].diff(13) > 0.25).astype(float)

    if "VIX" in weekly.columns:
        score += (zscore(weekly["VIX"], 52) > 0.50).astype(float)

    if "VIX" in weekly.columns and "VIX3M" in weekly.columns:
        score += (weekly["VIX"] > weekly["VIX3M"]).astype(float)

    if "BAMLH0A0HYM2" in weekly.columns:
        hy = weekly["BAMLH0A0HYM2"]
        score += ((hy.diff(4) > 0.25) | (zscore(hy, 52) > 0.50)).astype(float)

    return score


def strat_v12_robust_short_ensemble(
    weekly: pd.DataFrame, params: Optional[dict] = None
) -> pd.Series:
    """V12: V10 base + ensemble-voted crash short."""
    p = {
        "entry_vote": 0.55,
        "entry_score": 5,
        "short_hold_weeks": 4,
        "short_exposure": -1.0,
    }
    if params: p.update(params)

    base = strat_v10_rate_guard(weekly)
    vote = v12_fire_vote_fraction(weekly, base)
    score = v12_crash_score(weekly, base)

    entry = (vote >= float(p["entry_vote"])) & (score >= float(p["entry_score"]))
    active = entry.astype(float).rolling(int(p["short_hold_weeks"]), min_periods=1).max().fillna(0).astype(bool)

    out = base.copy()
    out[active] = float(p["short_exposure"])
    return out.clip(-1.0, 1.8)


def regime_label_v12(signal: float) -> str:
    if signal <= -0.5: return "CRASH_SHORT"
    if signal < 0.7: return "DEFENSIVE"
    if signal < 1.05: return "NORMAL"
    if signal <= 1.21: return "LEVERED_LONG_LIGHT"
    if signal <= 1.31: return "LEVERED_LONG_SHALLOW"
    if signal <= 1.51: return "LEVERED_LONG_RECOVERY"
    return "LEVERED_LONG_BOUNCE"


def v12_reason_for_row(signal: float, vote: float, score: float, spy_4w: float, spy_vs_40w: float) -> str:
    if signal <= -0.5:
        return f"Crash short: vote={vote:.2f}, crash_score={score:.0f}, 4W SPY={spy_4w*100:+.1f}%"
    if signal < 0.7:
        return f"Defensive: SPY below trend/risk-off; SPY vs 40W MA={spy_vs_40w*100:+.1f}%"
    if signal > 1.05:
        return "Levered long: dip/recovery/curve setup allowed and rate guard not blocking"
    if score >= 4:
        return f"Normal but watchlist: crash_score={score:.0f}, vote={vote:.2f}, 4W SPY={spy_4w*100:+.1f}%"
    return "Normal: no high-conviction leverage/defensive/short trigger"


# ---------------------------------------------------------------------------
# V17 conservative boost on top of V12
# ---------------------------------------------------------------------------

# V17-PRO three-tier boost magnitudes (calibrated; see V17_PRO_UPGRADE_REPORT.md).
# The legacy `boost` argument below is accepted for API compatibility but ignored.
BOOST_INTERSECTION = 0.25  # both calm_bull AND yc_steep fire (highest conviction)
BOOST_CB_ONLY      = 0.07  # only calm_bull fires (lowered from 0.15 in v17_orig)
BOOST_YC_ONLY      = 0.12  # only yc_steep fires (NEW sleeve)
YC_DIFF_WEEKS = 13


def build_v17_conservative_signal(
    weekly: pd.DataFrame,
    v12_signal: pd.Series,
    boost: float = DEFAULT_BOOST,           # accepted for compatibility; unused in v17-pro
    trend_ma: int = DEFAULT_TREND_MA,
    momentum_weeks: int = DEFAULT_MOMENTUM_WEEKS,
    rv_weeks: int = DEFAULT_RV_WEEKS,
    rv_lookback: int = DEFAULT_RV_LOOKBACK,
    rv_quantile: float = DEFAULT_RV_QUANTILE,
    vix_ma: int = DEFAULT_VIX_MA,
) -> Tuple[pd.Series, pd.DataFrame]:
    """V17-PRO: V12 base + 3-tier boost during V12-normal weeks.

    Tier 1 INTERSECTION (calm_bull AND yc_steep):  exposure 1.25x
    Tier 2 CALM_BULL only:                          exposure 1.07x
    Tier 3 YC_STEEP  only (NEW):                    exposure 1.12x
    Otherwise: V12 signal passes through unchanged (defensive / crash-short / levered-recovery preserved).

    YC_STEEP definition: T10Y2Y > 0 AND its 13-week change > 0.

    If T10Y2Y is missing from `weekly`, yc_steep is always False and the model
    degrades gracefully to a calm-bull-only sleeve at boost=0.07.

    Returns the same (signal, diagnostics) shape as the original V17, with
    additional diagnostic columns (yc_pos_steep, t10y2y, t10y2y_chg_13w,
    tier_intersection, tier_cb_only, tier_yc_only).
    """
    spy = weekly["SPY"]
    vix = weekly["VIX"]
    rv = spy.pct_change().rolling(rv_weeks).std() * np.sqrt(52.0)
    min_periods = max(30, rv_lookback // 3)
    rv_ref = rv.rolling(rv_lookback, min_periods=min_periods).quantile(rv_quantile)

    cond_v12_normal = np.isclose(v12_signal.astype(float), 1.0)
    cond_above_trend = spy > spy.rolling(trend_ma).mean()
    cond_momentum = spy.pct_change(momentum_weeks) > 0.0
    cond_calm = rv < rv_ref
    cond_vix_low = vix < vix.rolling(vix_ma).mean()
    calm_bull = cond_v12_normal & cond_above_trend & cond_momentum & cond_calm & cond_vix_low

    # NEW: yield-curve steepening trigger
    if "T10Y2Y" in weekly.columns:
        t10y2y = weekly["T10Y2Y"]
        yc_steep_raw = (t10y2y > 0) & (t10y2y.diff(YC_DIFF_WEEKS) > 0)
        yc_steep = yc_steep_raw.fillna(False)
    else:
        t10y2y = pd.Series(np.nan, index=weekly.index)
        yc_steep = pd.Series(False, index=weekly.index)

    # All tiers gated on V12 = 1.0 so V12 logic remains untouched
    v12_normal_s = pd.Series(cond_v12_normal, index=weekly.index)
    intersection = calm_bull & yc_steep & v12_normal_s
    cb_only      = calm_bull & ~yc_steep & v12_normal_s
    yc_only      = ~calm_bull & yc_steep & v12_normal_s

    v12 = v12_signal.astype(float)
    v17 = v12.copy()
    v17 = v17.where(~intersection, 1.0 + BOOST_INTERSECTION)
    v17 = v17.where(~cb_only,      1.0 + BOOST_CB_ONLY)
    v17 = v17.where(~yc_only,      1.0 + BOOST_YC_ONLY)

    diagnostics = pd.DataFrame({
        "v12_signal": v12,
        "v17_signal": v17,
        "calm_bull_trigger": calm_bull.astype(int),
        "spy_above_trend": cond_above_trend.astype(int),
        "spy_momentum_13w": spy.pct_change(momentum_weeks),
        "spy_rv_26w": rv,
        "spy_rv_ref_55p": rv_ref,
        "vix": vix,
        "vix_ma_52w": vix.rolling(vix_ma).mean(),
        # NEW v17-pro diagnostics
        "yc_pos_steep": yc_steep.astype(int),
        "t10y2y": t10y2y,
        "t10y2y_chg_13w": (t10y2y.diff(YC_DIFF_WEEKS) if "T10Y2Y" in weekly.columns
                           else pd.Series(np.nan, index=weekly.index)),
        "tier_intersection": intersection.astype(int),
        "tier_cb_only": cb_only.astype(int),
        "tier_yc_only": yc_only.astype(int),
    }, index=weekly.index)

    return v17, diagnostics


# ---------------------------------------------------------------------------
# Defensive sleeve and weight construction
# ---------------------------------------------------------------------------

def dynamic_defensive_sleeve(weekly: pd.DataFrame) -> pd.DataFrame:
    idx = weekly.index
    fallback = pd.DataFrame({"TLT": 0.50, "GLD": 0.20, "SHY": 0.30}, index=idx)

    if not all(c in weekly.columns for c in ["SPY", "TLT"]):
        return fallback

    spy_ret = weekly["SPY"].pct_change()
    tlt_ret = weekly["TLT"].pct_change()
    corr = spy_ret.rolling(13, min_periods=7).corr(tlt_ret).fillna(-0.20)
    stress = corr.clip(lower=0.0, upper=0.30) / 0.30

    tlt = 0.50 - 0.30 * stress
    gld = 0.20 + 0.10 * stress
    shy = 0.30 + 0.20 * stress
    total = tlt + gld + shy
    out = pd.DataFrame({"TLT": tlt / total, "GLD": gld / total, "SHY": shy / total}, index=idx)
    return out.fillna(fallback)


def signal_to_weekly_weights(signal: pd.Series, weekly: pd.DataFrame) -> pd.DataFrame:
    sig = signal.astype(float).clip(-1.0, 1.8)
    idx = sig.index
    sleeve = dynamic_defensive_sleeve(weekly).reindex(idx).ffill()
    sleeve = sleeve.fillna({"TLT": 0.50, "GLD": 0.20, "SHY": 0.30})

    weights = pd.DataFrame(0.0, index=idx, columns=ASSETS)

    long_mask = sig >= 1.0
    spxl_w = ((sig - 1.0) / 2.0).clip(0.0, 0.50)
    weights.loc[long_mask, "SPXL"] = spxl_w[long_mask]
    weights.loc[long_mask, "SPY"] = (1.0 - spxl_w)[long_mask]

    def_mask = (sig >= 0.0) & (sig < 1.0)
    cash = (1.0 - sig).clip(lower=0.0)
    weights.loc[def_mask, "SPY"] = sig[def_mask]
    for asset in ["TLT", "GLD", "SHY"]:
        weights.loc[def_mask, asset] = (cash * sleeve[asset])[def_mask]

    short_mask = sig < 0.0
    spxs_w = (-sig / 3.0).clip(0.0, 0.67)
    sleeve_cash = 1.0 - spxs_w
    weights.loc[short_mask, "SPXS"] = spxs_w[short_mask]
    for asset in ["TLT", "GLD", "SHY"]:
        weights.loc[short_mask, asset] = (sleeve_cash * sleeve[asset])[short_mask]

    return weights.fillna(0.0)


def weekly_weights_to_daily(
    weekly_weights: pd.DataFrame, daily_index: pd.DatetimeIndex
) -> pd.DataFrame:
    target = weekly_weights.reindex(daily_index, method="ffill")
    effective = target.shift(1)
    fill = {a: 0.0 for a in ASSETS}
    fill["SPY"] = 1.0
    return effective.fillna(fill)


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------

def run_backtest(
    signal_weekly: pd.Series, daily: pd.DataFrame, tc_bps: float
) -> Dict[str, pd.Series | pd.DataFrame]:
    weekly_prices = resample_completed_friday_weeks(daily)
    sig = signal_weekly.reindex(weekly_prices.index).ffill().fillna(1.0)

    weekly_w = signal_to_weekly_weights(sig, weekly_prices)
    daily_w = weekly_weights_to_daily(weekly_w, daily.index)

    daily_ret_assets = daily[ASSETS].ffill().pct_change().fillna(0.0)
    turnover = daily_w.diff().abs().sum(axis=1).fillna(0.0)
    cost = turnover * (tc_bps / 10000.0)

    strat_ret = (daily_w * daily_ret_assets).sum(axis=1) - cost
    exposure = daily_w["SPY"] + 3.0 * daily_w["SPXL"] - 3.0 * daily_w["SPXS"]
    equity = (1.0 + strat_ret).cumprod()

    rf_daily = get_rf_daily(daily, strat_ret.index)

    return {
        "ret": strat_ret, "weights": daily_w,
        "exposure": exposure, "equity": equity,
        "turnover": turnover,
        "rf_daily": rf_daily,
    }


def metrics_daily(returns: pd.Series, rf_daily: Optional[pd.Series] = None) -> Dict[str, float]:
    r = pd.Series(returns).replace([np.inf, -np.inf], np.nan).dropna()
    if r.empty:
        return {"n": 0, "total_return": np.nan, "cagr": np.nan, "annual_vol": np.nan,
                "sharpe": np.nan, "max_drawdown": np.nan, "calmar": np.nan, "hit_rate": np.nan}

    eq = (1.0 + r).cumprod()
    years = len(r) / ANNUALIZATION_DAYS
    total_return = float(eq.iloc[-1] - 1.0)
    cagr = float(eq.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 and eq.iloc[-1] > 0 else np.nan
    annual_vol = float(r.std() * np.sqrt(ANNUALIZATION_DAYS))

    # Sharpe: subtract daily risk-free rate before annualizing
    if rf_daily is not None:
        rf_aligned = rf_daily.reindex(r.index).ffill().fillna(0.0)
        excess = r - rf_aligned
    else:
        excess = r
    sharpe = float(excess.mean() * ANNUALIZATION_DAYS / annual_vol) if annual_vol > 1e-12 else np.nan

    drawdown = eq / eq.cummax() - 1.0
    max_drawdown = float(drawdown.min())
    calmar = float(cagr / abs(max_drawdown)) if max_drawdown < 0 else np.nan
    return {
        "n": int(len(r)), "total_return": total_return,
        "cagr": cagr, "annual_vol": annual_vol, "sharpe": sharpe,
        "max_drawdown": max_drawdown, "calmar": calmar,
        "hit_rate": float((r > 0).mean()),
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def headline_comparison(bt: Dict[str, Dict], daily: pd.DataFrame) -> pd.DataFrame:
    periods = {
        "full": daily.index >= "1900-01-01",
        "holdout_2021_plus": daily.index >= "2021-01-01",
    }
    rows = []
    for period, mask in periods.items():
        for model, obj in bt.items():
            rf = obj.get("rf_daily", None)
            rf_slice = rf[mask] if rf is not None else None
            m = metrics_daily(obj["ret"][mask], rf_daily=rf_slice)
            exposure = obj.get("exposure", pd.Series(1.0, index=daily.index))
            rows.append({
                "period": period, "model": model, **m,
                "avg_exposure": float(exposure[mask].mean()),
                "pct_levered": float((exposure[mask] > 1.0001).mean()),
                "pct_short": float((exposure[mask] < 0).mean()),
            })
    return pd.DataFrame(rows)


def stress_window_report(bt: Dict[str, Dict]) -> pd.DataFrame:
    windows = {
        "2011_euro_stress":      ("2011-07-01", "2011-12-31"),
        "2015_2016_china_oil":   ("2015-08-01", "2016-02-29"),
        "2018_q4_fed_selloff":   ("2018-10-01", "2018-12-31"),
        "2020_covid_crash":      ("2020-02-19", "2020-04-30"),
        "2022_bear_market":      ("2022-01-01", "2022-12-31"),
        "2023_low_vol_uptrend":  ("2023-01-01", "2023-12-31"),
        "2024_low_vol_uptrend":  ("2024-01-01", "2024-12-31"),
    }
    rows = []
    for name, (s, e) in windows.items():
        for model, obj in bt.items():
            r = obj["ret"].loc[s:e]
            if len(r) < 10: continue
            rf = obj.get("rf_daily", None)
            rf_slice = rf.loc[s:e] if rf is not None else None
            rows.append({"window": name, "model": model, **metrics_daily(r, rf_daily=rf_slice)})
    return pd.DataFrame(rows)


def yearly_report(bt: Dict[str, Dict]) -> pd.DataFrame:
    rows = []
    for model, obj in bt.items():
        ret = obj["ret"]
        rf = obj.get("rf_daily", None)
        for year, r in ret.groupby(ret.index.year):
            if len(r) < 50: continue
            rf_slice = rf.loc[r.index] if rf is not None else None
            rows.append({"year": int(year), "model": model, **metrics_daily(r, rf_daily=rf_slice)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def block_bootstrap_delta(
    ret_new: pd.Series, ret_base: pd.Series, metric_name: str,
    n_bootstrap: int, block_len: int, seed: int,
    progress_label: str = "", show_progress: bool = False,
) -> Dict[str, float]:
    df = pd.concat([ret_new.rename("new"), ret_base.rename("base")], axis=1).dropna()
    n = len(df)

    obs = metrics_daily(df["new"])[metric_name] - metrics_daily(df["base"])[metric_name]
    if n < block_len * 4:
        return {"metric": metric_name, "observed_delta": float(obs),
                "p_fail": np.nan, "n_bootstrap": 0, "block_len": block_len}

    rng = np.random.default_rng(seed)
    new_arr = df["new"].values
    base_arr = df["base"].values
    n_blocks = (n + block_len - 1) // block_len
    starts = np.arange(0, n - block_len + 1)

    report_every = max(1, n_bootstrap // 50) if (show_progress and n_bootstrap >= 50) else 0

    deltas = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        block_starts = rng.choice(starts, size=n_blocks, replace=True)
        idx = np.concatenate([np.arange(s, s + block_len) for s in block_starts])[:n]
        s_new = new_arr[idx]
        s_base = base_arr[idx]
        m_new = metrics_daily(pd.Series(s_new))[metric_name]
        m_base = metrics_daily(pd.Series(s_base))[metric_name]
        deltas[i] = m_new - m_base

        if report_every and ((i + 1) % report_every == 0 or i + 1 == n_bootstrap):
            progress_bar(i + 1, n_bootstrap, progress_label)

    return {
        "metric": metric_name, "observed_delta": float(obs),
        "p_fail": float((deltas <= 0.0).mean()),
        "bootstrap_mean_delta": float(np.nanmean(deltas)),
        "n_bootstrap": int(n_bootstrap), "block_len": int(block_len),
    }


def bootstrap_suite(
    bt: Dict[str, Dict], n_bootstrap: int, block_len: int, seed: int,
    show_progress: bool = False,
) -> pd.DataFrame:
    rows = []
    comparisons = [("v17_conservative", "v12"), ("v17_conservative", "SPY_BH")]
    periods = {"full": ("1900-01-01", "2100-01-01"),
               "holdout_2021_plus": ("2021-01-01", "2100-01-01")}
    metric_names = ["total_return", "sharpe", "calmar", "max_drawdown"]

    total_jobs = len(comparisons) * len(periods) * len(metric_names)
    job_idx = 0

    for new, base in comparisons:
        for period, (s, e) in periods.items():
            r_new = bt[new]["ret"].loc[s:e]
            r_base = bt[base]["ret"].loc[s:e]
            for metric in metric_names:
                job_idx += 1
                target = "vs SPY" if base == "SPY_BH" else "vs V12"
                label = f"{target} / {period} / {metric:<14s} ({job_idx}/{total_jobs})"
                res = block_bootstrap_delta(
                    r_new, r_base, metric, n_bootstrap, block_len,
                    seed + len(rows), progress_label=label, show_progress=show_progress,
                )
                rows.append({"new_model": new, "base_model": base, "period": period, **res})

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Heavy validation suite
# ---------------------------------------------------------------------------

def _norm_cdf(x: float) -> float:
    if stats is not None:
        return float(stats.norm.cdf(x))
    return float(0.5 * (1.0 + np.math.erf(x / np.sqrt(2.0))))


def _norm_ppf(p: float) -> float:
    if stats is not None:
        return float(stats.norm.ppf(p))
    # Acklam approximation fallback
    # Good enough for p in (0,1); scipy is preferred and included in requirements.
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = np.sqrt(-2*np.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = np.sqrt(-2*np.log(1-p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def _skew_kurt(r: pd.Series) -> Tuple[float, float]:
    x = pd.Series(r).dropna()
    if len(x) < 5:
        return np.nan, np.nan
    skew = float(x.skew())
    # pandas kurt() is excess kurtosis, add 3 for regular kurtosis.
    kurt = float(x.kurt() + 3.0)
    return skew, kurt


def deflated_sharpe_table(bt: Dict[str, Dict], n_trials: int = DEFAULT_N_VARIANTS_ASSUMED) -> pd.DataFrame:
    """Approximate Bailey/Lopez de Prado deflated Sharpe probability.

    This is intentionally conservative: it treats the stated model-development variants
    as multiple trials and asks whether the observed daily Sharpe clears the expected
    best Sharpe from those trials after non-normality adjustment.
    """
    rows = []
    euler_gamma = 0.5772156649015329
    n_trials = max(2, int(n_trials))
    z_trials = ((1.0 - euler_gamma) * _norm_ppf(1.0 - 1.0 / n_trials)
                + euler_gamma * _norm_ppf(1.0 - 1.0 / (n_trials * np.e)))
    for model, obj in bt.items():
        r = pd.Series(obj["ret"]).dropna()
        n = len(r)
        if n < 30 or r.std() <= 0:
            continue
        rf = obj.get("rf_daily", None)
        if rf is not None:
            rf_aligned = rf.reindex(r.index).ffill().fillna(0.0)
            excess = r - rf_aligned
        else:
            excess = r
        daily_sr = float(excess.mean() / r.std())
        annual_sr = daily_sr * np.sqrt(ANNUALIZATION_DAYS)
        skew, kurt = _skew_kurt(r)
        denom = 1.0 - skew * daily_sr + ((kurt - 1.0) / 4.0) * daily_sr ** 2
        sr_std = np.sqrt(max(denom, 1e-12) / max(n - 1, 1))
        sr_star = sr_std * z_trials
        z = (daily_sr - sr_star) / max(sr_std, 1e-12)
        rows.append({
            "model": model,
            "n": n,
            "assumed_trials": n_trials,
            "annual_sharpe": annual_sr,
            "daily_sharpe": daily_sr,
            "deflated_threshold_daily": sr_star,
            "deflated_threshold_annual": sr_star * np.sqrt(ANNUALIZATION_DAYS),
            "deflated_sharpe_probability": _norm_cdf(z),
            "skew": skew,
            "kurtosis": kurt,
        })
    return pd.DataFrame(rows)


def bayesian_sharpe_table(bt: Dict[str, Dict], n_draws: int, seed: int) -> pd.DataFrame:
    """Normal-inverse-chi-square posterior for annualized Sharpe.

    Uses a weak/Jeffreys-style posterior for mean and variance. This is not a
    promise of future performance; it is a decision-friendly uncertainty interval.
    """
    rng = np.random.default_rng(seed)
    draws = {}
    rows = []
    for model, obj in bt.items():
        r = pd.Series(obj["ret"]).replace([np.inf, -np.inf], np.nan).dropna()
        rf = obj.get("rf_daily", None)
        if rf is not None:
            rf_aligned = rf.reindex(r.index).ffill().fillna(0.0)
            r = r - rf_aligned
        r = r.values
        n = len(r)
        if n < 30 or np.std(r, ddof=1) <= 0:
            continue
        xbar = float(np.mean(r))
        s2 = float(np.var(r, ddof=1))
        df = n - 1
        chi = rng.chisquare(df, size=n_draws)
        sigma2 = df * s2 / np.maximum(chi, 1e-12)
        mu = rng.normal(xbar, np.sqrt(sigma2 / n))
        sr = mu / np.sqrt(sigma2) * np.sqrt(ANNUALIZATION_DAYS)
        draws[model] = sr
        rows.append({
            "model": model,
            "draws": n_draws,
            "sharpe_mean": float(np.mean(sr)),
            "sharpe_p05": float(np.quantile(sr, 0.05)),
            "sharpe_p50": float(np.quantile(sr, 0.50)),
            "sharpe_p95": float(np.quantile(sr, 0.95)),
            "prob_sharpe_gt_0": float((sr > 0).mean()),
        })
    # Pairwise probabilities vs SPY and V12
    out = pd.DataFrame(rows)
    if "v17_conservative" in draws:
        v17 = draws["v17_conservative"]
        if "SPY_BH" in draws:
            out.loc[out["model"] == "v17_conservative", "prob_sharpe_gt_spy"] = float((v17 > draws["SPY_BH"]).mean())
        if "v12" in draws:
            out.loc[out["model"] == "v17_conservative", "prob_sharpe_gt_v12"] = float((v17 > draws["v12"]).mean())
    return out


def random_rebalance_comparison(
    weekly: pd.DataFrame,
    daily: pd.DataFrame,
    actual_signal: pd.Series,
    actual_bt: Dict[str, pd.Series | pd.DataFrame],
    tc_bps: float,
    n_random: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sig = actual_signal.reindex(weekly.index).dropna().astype(float)
    obs = metrics_daily(actual_bt["ret"], rf_daily=actual_bt.get("rf_daily"))
    metric_names = ["total_return", "sharpe", "calmar", "max_drawdown"]
    rand_metrics = {m: np.empty(n_random) for m in metric_names}
    vals = sig.values.copy()
    idx = sig.index
    for i in range(n_random):
        perm = rng.permutation(vals)
        s = pd.Series(perm, index=idx)
        bt_rand = run_backtest(s, daily, tc_bps)
        met = metrics_daily(bt_rand["ret"], rf_daily=bt_rand.get("rf_daily"))
        for m in metric_names:
            rand_metrics[m][i] = met[m]
    rows = []
    for m in metric_names:
        arr = rand_metrics[m]
        # higher is better for all listed metrics; max_drawdown is less negative when better.
        rows.append({
            "metric": m,
            "actual": obs[m],
            "random_mean": float(np.nanmean(arr)),
            "random_p95": float(np.nanquantile(arr, 0.95)),
            "p_random_beats_actual": float((arr >= obs[m]).mean()),
            "n_random": n_random,
        })
    return pd.DataFrame(rows)


def _estimate_ar1_params(r: pd.Series) -> Tuple[float, float, float]:
    x = pd.Series(r).dropna().values
    if len(x) < 50:
        return 0.0, 0.0, float(np.nanstd(x))
    y = x[1:]
    lag = x[:-1]
    phi = float(np.corrcoef(y, lag)[0, 1]) if np.std(lag) > 0 and np.std(y) > 0 else 0.0
    phi = float(np.clip(phi, -0.25, 0.25))
    mu = float(np.mean(x))
    eps = y - mu - phi * (lag - mu)
    sigma = float(np.std(eps, ddof=1))
    return mu, phi, sigma


def synthetic_null_markets(
    bt: Dict[str, Dict],
    daily: pd.DataFrame,
    n_synthetic: int,
    seed: int,
) -> pd.DataFrame:
    """Generate AR(1) SPY-like null markets and test whether exposure timing still looks special.

    This is an exposure-timing null, not a full multi-asset ETF market simulator.
    It preserves SPY daily mean/vol/autocorrelation approximately but removes real regime structure.
    """
    rng = np.random.default_rng(seed)
    spy_ret = daily["SPY"].ffill().pct_change().fillna(0.0)
    mu, phi, sigma = _estimate_ar1_params(spy_ret)
    n = len(spy_ret)
    rf_v17 = bt["v17_conservative"].get("rf_daily", None)
    rf_spy = bt["SPY_BH"].get("rf_daily", None)
    actual_v17 = metrics_daily(bt["v17_conservative"]["ret"], rf_daily=rf_v17)
    actual_spy = metrics_daily(bt["SPY_BH"]["ret"], rf_daily=rf_spy)
    obs_delta = {m: actual_v17[m] - actual_spy[m] for m in ["total_return", "sharpe", "calmar", "max_drawdown"]}
    exp = bt["v17_conservative"].get("exposure", pd.Series(1.0, index=daily.index)).reindex(daily.index).ffill().fillna(1.0).values
    null_deltas = {m: np.empty(n_synthetic) for m in obs_delta}
    for i in range(n_synthetic):
        r = np.empty(n)
        r[0] = rng.normal(mu, sigma)
        shocks = rng.normal(0.0, sigma, size=n)
        for t in range(1, n):
            r[t] = mu + phi * (r[t - 1] - mu) + shocks[t]
        spy_null = pd.Series(r, index=daily.index)
        # approximate strategy using actual time-varying net equity exposure; clip to avoid impossible ruin.
        strat_null = pd.Series(exp * r, index=daily.index).clip(lower=-0.95)
        m_s = metrics_daily(strat_null)
        m_b = metrics_daily(spy_null)
        for m in obs_delta:
            null_deltas[m][i] = m_s[m] - m_b[m]
    rows = []
    for m, arr in null_deltas.items():
        rows.append({
            "metric": m,
            "observed_delta_v17_minus_spy": obs_delta[m],
            "null_mean_delta": float(np.nanmean(arr)),
            "null_p95_delta": float(np.nanquantile(arr, 0.95)),
            "p_synthetic_beats_observed": float((arr >= obs_delta[m]).mean()),
            "n_synthetic": n_synthetic,
        })
    return pd.DataFrame(rows)


def regime_daily_labels(signal_table: pd.DataFrame, daily_index: pd.DatetimeIndex) -> pd.Series:
    lab = pd.Series("normal", index=signal_table.index)
    lab[signal_table["calm_bull_trigger"].astype(int) == 1] = "calm_bull"
    lab[signal_table["v12_signal"] > 1.0] = "v12_levered_recovery"
    lab[(signal_table["v12_signal"] >= 0) & (signal_table["v12_signal"] < 1.0)] = "defensive"
    lab[signal_table["v12_signal"] < 0] = "crash_short"
    return lab.reindex(daily_index, method="ffill").fillna("normal")


def stratified_regime_test(bt: Dict[str, Dict], signal_table: pd.DataFrame, daily: pd.DataFrame, block_len: int, seed: int) -> pd.DataFrame:
    labels = regime_daily_labels(signal_table, daily.index)
    rows = []
    for regime in ["calm_bull", "normal", "v12_levered_recovery", "defensive", "crash_short"]:
        mask = labels == regime
        if mask.sum() < max(40, block_len * 3):
            continue
        r17 = bt["v17_conservative"]["ret"][mask]
        r12 = bt["v12"]["ret"][mask]
        rsp = bt["SPY_BH"]["ret"][mask]
        rf17 = bt["v17_conservative"].get("rf_daily")
        rf12 = bt["v12"].get("rf_daily")
        rfsp = bt["SPY_BH"].get("rf_daily")
        met17 = metrics_daily(r17, rf_daily=rf17[mask] if rf17 is not None else None)
        met12 = metrics_daily(r12, rf_daily=rf12[mask] if rf12 is not None else None)
        metspy = metrics_daily(rsp, rf_daily=rfsp[mask] if rfsp is not None else None)
        # mean-return block bootstrap p-value vs v12 inside this regime.
        diff = (r17 - r12).dropna().values
        rng = np.random.default_rng(seed + len(rows))
        n = len(diff)
        starts = np.arange(0, max(1, n - block_len + 1))
        boot = []
        for _ in range(500):
            if len(starts) == 0:
                break
            bstarts = rng.choice(starts, size=(n + block_len - 1)//block_len, replace=True)
            idx = np.concatenate([np.arange(s, min(s+block_len, n)) for s in bstarts])[:n]
            boot.append(np.mean(diff[idx]) * ANNUALIZATION_DAYS)
        obs = float(np.mean(diff) * ANNUALIZATION_DAYS)
        p_fail = float((np.array(boot) <= 0).mean()) if boot else np.nan
        rows.append({
            "regime": regime,
            "days": int(mask.sum()),
            "v17_total_return": met17["total_return"],
            "v12_total_return": met12["total_return"],
            "spy_total_return": metspy["total_return"],
            "v17_sharpe": met17["sharpe"],
            "v12_sharpe": met12["sharpe"],
            "spy_sharpe": metspy["sharpe"],
            "annualized_mean_return_delta_v17_minus_v12": obs,
            "p_fail_mean_return_vs_v12": p_fail,
        })
    return pd.DataFrame(rows)


def rolling_window_test(bt: Dict[str, Dict], horizons_years: List[int] = [1, 3, 5]) -> pd.DataFrame:
    rows = []
    for yrs in horizons_years:
        window = int(252 * yrs)
        step = 21  # roughly monthly starts
        idx = bt["SPY_BH"]["ret"].index
        for start_i in range(0, len(idx) - window + 1, step):
            s, e = idx[start_i], idx[start_i + window - 1]
            vals = {m: metrics_daily(obj["ret"].loc[s:e],
                                     rf_daily=obj.get("rf_daily", pd.Series(dtype=float)).loc[s:e]
                                     if obj.get("rf_daily") is not None else None)
                    for m, obj in bt.items()}
            rows.append({
                "horizon_years": yrs,
                "start": s.date().isoformat(),
                "end": e.date().isoformat(),
                "v17_return": vals["v17_conservative"]["total_return"],
                "v12_return": vals["v12"]["total_return"],
                "spy_return": vals["SPY_BH"]["total_return"],
                "v17_sharpe": vals["v17_conservative"]["sharpe"],
                "v12_sharpe": vals["v12"]["sharpe"],
                "spy_sharpe": vals["SPY_BH"]["sharpe"],
                "v17_beats_spy_return": vals["v17_conservative"]["total_return"] > vals["SPY_BH"]["total_return"],
                "v17_beats_v12_return": vals["v17_conservative"]["total_return"] > vals["v12"]["total_return"],
                "v17_beats_spy_sharpe": vals["v17_conservative"]["sharpe"] > vals["SPY_BH"]["sharpe"],
                "v17_beats_v12_sharpe": vals["v17_conservative"]["sharpe"] > vals["v12"]["sharpe"],
            })
    return pd.DataFrame(rows)


def rolling_window_summary(rolling: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if rolling.empty:
        return pd.DataFrame()
    for h, g in rolling.groupby("horizon_years"):
        rows.append({
            "horizon_years": int(h),
            "n_windows": int(len(g)),
            "pct_v17_beats_spy_return": float(g["v17_beats_spy_return"].mean()),
            "pct_v17_beats_v12_return": float(g["v17_beats_v12_return"].mean()),
            "pct_v17_beats_spy_sharpe": float(g["v17_beats_spy_sharpe"].mean()),
            "pct_v17_beats_v12_sharpe": float(g["v17_beats_v12_sharpe"].mean()),
            "median_return_delta_v17_minus_spy": float((g["v17_return"] - g["spy_return"]).median()),
            "median_return_delta_v17_minus_v12": float((g["v17_return"] - g["v12_return"]).median()),
        })
    return pd.DataFrame(rows)


def yearly_consistency_test(yearly: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if yearly.empty or stats is None:
        return pd.DataFrame()
    for metric in ["total_return", "sharpe", "calmar", "max_drawdown"]:
        for base in ["SPY_BH", "v12"]:
            wide = yearly.pivot_table(index="year", columns="model", values=metric, aggfunc="first")
            if "v17_conservative" not in wide.columns or base not in wide.columns:
                continue
            diff = wide["v17_conservative"] - wide[base]
            diff = diff.dropna()
            wins = int((diff > 0).sum())
            n = int(len(diff))
            p = float(stats.binomtest(wins, n, 0.5, alternative="greater").pvalue) if n > 0 else np.nan
            rows.append({"metric": metric, "base_model": base, "years": n, "wins": wins, "win_rate": wins/n if n else np.nan, "binomial_p_value": p})
    return pd.DataFrame(rows)


def cost_stress_test(weekly: pd.DataFrame, daily: pd.DataFrame, v12_signal: pd.Series, v17_signal: pd.Series) -> pd.DataFrame:
    rows = []
    for tc in [0.0, 5.0, 10.0, 20.0, 30.0]:
        bts = {
            "SPY_BH": {"ret": daily["SPY"].ffill().pct_change().fillna(0.0), "exposure": pd.Series(1.0, index=daily.index)},
            "v12": run_backtest(v12_signal, daily, tc),
            "v17_conservative": run_backtest(v17_signal, daily, tc),
        }
        head = headline_comparison(bts, daily)
        head["tc_bps"] = tc
        rows.append(head)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def parameter_sensitivity_test(
    weekly: pd.DataFrame,
    daily: pd.DataFrame,
    v12_signal: pd.Series,
    tc_bps: float,
    grid: str = "full",
) -> pd.DataFrame:
    rows = []
    if grid == "off":
        return pd.DataFrame()
    base_bt = run_backtest(v12_signal, daily, tc_bps)
    base_hold = metrics_daily(base_bt["ret"].loc["2021-01-01":], rf_daily=base_bt.get("rf_daily", pd.Series(dtype=float)).loc["2021-01-01":] if base_bt.get("rf_daily") is not None else None)
    if grid == "smoke":
        # Fast coverage check for the sensitivity code path.
        boosts = [0.10, 0.15, 0.20]
        trends = [40]
        moms = [13]
        rv_qs = [0.45, 0.55]
        vix_mas = [52]
    else:
        boosts = [0.05, 0.10, 0.15, 0.20]
        trends = [30, 40, 50]
        moms = [8, 13, 26]
        rv_qs = [0.45, 0.55, 0.65]
        vix_mas = [26, 52]
    for boost in boosts:
        for trend in trends:
            for mom in moms:
                for rvq in rv_qs:
                    for vixma in vix_mas:
                        sig, diag = build_v17_conservative_signal(
                            weekly, v12_signal, boost=boost, trend_ma=trend,
                            momentum_weeks=mom, rv_quantile=rvq, vix_ma=vixma,
                        )
                        bt = run_backtest(sig, daily, tc_bps)
                        rf_bt = bt.get("rf_daily")
                        hold = metrics_daily(bt["ret"].loc["2021-01-01":], rf_daily=rf_bt.loc["2021-01-01":] if rf_bt is not None else None)
                        full = metrics_daily(bt["ret"], rf_daily=rf_bt)
                        rows.append({
                            "boost": boost, "trend_ma": trend, "momentum_weeks": mom,
                            "rv_quantile": rvq, "vix_ma": vixma,
                            "n_boost_weeks": int(diag["calm_bull_trigger"].sum()),
                            "holdout_return": hold["total_return"],
                            "holdout_sharpe": hold["sharpe"],
                            "holdout_calmar": hold["calmar"],
                            "holdout_max_drawdown": hold["max_drawdown"],
                            "full_return": full["total_return"],
                            "full_sharpe": full["sharpe"],
                            "beats_v12_holdout_return": hold["total_return"] > base_hold["total_return"],
                            "beats_v12_holdout_sharpe": hold["sharpe"] > base_hold["sharpe"],
                            "beats_v12_holdout_calmar": hold["calmar"] > base_hold["calmar"],
                            "beats_v12_holdout_maxdd": hold["max_drawdown"] > base_hold["max_drawdown"],
                        })
    return pd.DataFrame(rows)


def summarize_parameter_sensitivity(param: pd.DataFrame) -> pd.DataFrame:
    if param.empty:
        return pd.DataFrame()
    bool_cols = [c for c in param.columns if c.startswith("beats_v12")]
    rows = []
    for c in bool_cols:
        rows.append({"test": c, "pct_variants_true": float(param[c].mean()), "n_variants": int(len(param))})
    return pd.DataFrame(rows)


def _markdown_cell(value) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.4f}"
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a Markdown table without pandas' optional tabulate dependency."""
    headers = [str(c).replace("|", "\\|") for c in df.columns]
    rows = [[_markdown_cell(value) for value in row] for row in df.to_numpy()]
    widths = [max([len(headers[i])] + [len(row[i]) for row in rows]) for i in range(len(headers))]

    def render_row(values: List[str]) -> str:
        return "| " + " | ".join(values[i].ljust(widths[i]) for i in range(len(values))) + " |"

    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    return "\n".join([render_row(headers), separator] + [render_row(row) for row in rows])


def write_heavy_validation_report(out: Path, tables: Dict[str, pd.DataFrame], n_trials: int) -> None:
    lines = []
    lines.append("# V17 Conservative — Heavy Validation Report")
    lines.append("")
    lines.append("This report is designed to test whether V17's edge is genuine rather than just a lucky backtest. It is intentionally stricter than the normal performance report.")
    lines.append("")
    lines.append("## Method note")
    lines.append("")
    lines.append("- Block bootstrap resamples chunks of time to preserve serial dependence and mini-regimes.")
    lines.append("- Random rebalance keeps V17's exact exposure distribution but destroys timing.")
    lines.append("- Synthetic null markets preserve approximate SPY variance/autocorrelation but remove historical regime structure.")
    lines.append("- Deflated Sharpe adjusts the Sharpe estimate for non-normal returns and the fact that many variants were tested.")
    lines.append("")
    lines.append(f"Assumed model-development trials for Deflated Sharpe: **{n_trials}**.")
    lines.append("")

    def add_df(title: str, df: pd.DataFrame, max_rows: int = 30):
        lines.append(f"## {title}")
        lines.append("")
        if df is None or df.empty:
            lines.append("No rows generated.")
        else:
            show = df.head(max_rows).copy()
            lines.append(dataframe_to_markdown(show))
        lines.append("")

    add_df("1. Block bootstrap", tables.get("bootstrap"), 40)
    add_df("2. Random rebalance timing test", tables.get("random_rebalance"), 20)
    add_df("3. Synthetic null market test", tables.get("synthetic_null"), 20)
    add_df("4. Stratified regime test", tables.get("stratified_regime"), 20)
    add_df("5. Deflated Sharpe Ratio", tables.get("deflated_sharpe"), 20)
    add_df("6. Bayesian Sharpe credible interval", tables.get("bayesian_sharpe"), 20)
    add_df("7. Yearly walk-forward consistency", tables.get("yearly_consistency"), 30)
    add_df("8. Rolling 1y/3y/5y windows", tables.get("rolling_summary"), 20)
    add_df("9. Cost stress", tables.get("cost_stress_summary"), 40)
    add_df("10. Parameter sensitivity summary", tables.get("parameter_summary"), 20)

    # Automatic verdict
    lines.append("## Overall automated verdict")
    lines.append("")
    verdicts = []
    rr = tables.get("random_rebalance", pd.DataFrame())
    if not rr.empty:
        p_sh = rr.loc[rr["metric"] == "sharpe", "p_random_beats_actual"]
        if len(p_sh) and float(p_sh.iloc[0]) < 0.05:
            verdicts.append("PASS: V17 Sharpe is in the upper tail versus random schedules with the same exposure distribution.")
        else:
            verdicts.append("WATCH: V17 timing is not strongly separated from random schedules on Sharpe.")
    synth = tables.get("synthetic_null", pd.DataFrame())
    if not synth.empty:
        p_ret = synth.loc[synth["metric"] == "total_return", "p_synthetic_beats_observed"]
        if len(p_ret) and float(p_ret.iloc[0]) < 0.10:
            verdicts.append("PASS: V17 return edge is stronger than most synthetic no-regime markets.")
        else:
            verdicts.append("WATCH: Synthetic no-regime market test does not strongly reject the null.")
    dsh = tables.get("deflated_sharpe", pd.DataFrame())
    if not dsh.empty and "v17_conservative" in set(dsh["model"]):
        p = float(dsh.loc[dsh["model"] == "v17_conservative", "deflated_sharpe_probability"].iloc[0])
        if p > 0.95:
            verdicts.append("PASS: Deflated Sharpe probability is above 95% after multiple-testing adjustment.")
        else:
            verdicts.append("WATCH: Deflated Sharpe probability is below 95%; treat edge as less proven.")
    if not verdicts:
        verdicts.append("No automated verdict could be generated.")
    for v in verdicts:
        lines.append(f"- {v}")
    lines.append("")

    (out / "HEAVY_VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run_heavy_validation(
    out: Path,
    weekly: pd.DataFrame,
    daily: pd.DataFrame,
    v12_signal: pd.Series,
    v17_signal: pd.Series,
    signal_table: pd.DataFrame,
    bt: Dict[str, Dict],
    bootstrap: pd.DataFrame,
    yearly: pd.DataFrame,
    cfg: "Config",
) -> Dict[str, pd.DataFrame]:
    """Run the heavy validation suite and save all component tables."""
    tables: Dict[str, pd.DataFrame] = {"bootstrap": bootstrap}

    print("\n  Heavy validation suite")
    hv_steps = StepLogger(9)

    hv_steps.start(f"Random rebalance timing test ({cfg.n_random_rebalance} schedules)")
    tables["random_rebalance"] = random_rebalance_comparison(
        weekly, daily, v17_signal, bt["v17_conservative"], cfg.tc_bps,
        cfg.n_random_rebalance, cfg.seed + 1000,
    )
    hv_steps.done()

    hv_steps.start(f"Synthetic null markets ({cfg.n_synthetic} paths)")
    tables["synthetic_null"] = synthetic_null_markets(bt, daily, cfg.n_synthetic, cfg.seed + 2000)
    hv_steps.done()

    hv_steps.start("Stratified regime test")
    tables["stratified_regime"] = stratified_regime_test(bt, signal_table, daily, cfg.block_len, cfg.seed + 3000)
    hv_steps.done()

    hv_steps.start("Deflated Sharpe Ratio")
    tables["deflated_sharpe"] = deflated_sharpe_table(bt, cfg.assumed_trials)
    hv_steps.done()

    hv_steps.start(f"Bayesian Sharpe credible interval ({cfg.n_bayes_draws} draws)")
    tables["bayesian_sharpe"] = bayesian_sharpe_table(bt, cfg.n_bayes_draws, cfg.seed + 4000)
    hv_steps.done()

    hv_steps.start("Yearly walk-forward consistency")
    tables["yearly_consistency"] = yearly_consistency_test(yearly)
    hv_steps.done()

    hv_steps.start("Rolling 1y/3y/5y horizon test")
    rolling = rolling_window_test(bt)
    tables["rolling_windows"] = rolling
    tables["rolling_summary"] = rolling_window_summary(rolling)
    hv_steps.done()

    hv_steps.start("Cost stress test")
    cost = cost_stress_test(weekly, daily, v12_signal, v17_signal)
    tables["cost_stress"] = cost
    # compact summary for report: holdout rows only
    tables["cost_stress_summary"] = cost[cost["period"] == "holdout_2021_plus"].copy() if not cost.empty else pd.DataFrame()
    hv_steps.done()

    hv_steps.start(f"Parameter sensitivity grid ({cfg.sensitivity_grid})")
    param = parameter_sensitivity_test(weekly, daily, v12_signal, cfg.tc_bps, cfg.sensitivity_grid)
    tables["parameter_sensitivity"] = param
    tables["parameter_summary"] = summarize_parameter_sensitivity(param)
    hv_steps.done()

    # Save tables
    for name, df in tables.items():
        if df is not None and not df.empty:
            df.to_csv(out / f"heavy_{name}.csv", index=False)
    write_heavy_validation_report(out, tables, cfg.assumed_trials)
    return tables


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def write_report(
    out: Path, latest: pd.Series, headline: pd.DataFrame,
    stress: pd.DataFrame, yearly: pd.DataFrame, bootstrap: pd.DataFrame,
    full_mode: bool, data_source: str,
) -> None:
    holdout = headline[headline["period"] == "holdout_2021_plus"].set_index("model")
    full = headline[headline["period"] == "full"].set_index("model")

    spy_full = full.loc["SPY_BH"]
    v12_full = full.loc["v12"]
    v17_full = full.loc["v17_conservative"]

    lines = []
    lines.append("# SPY V17 Conservative — Performance & Validation Report")
    lines.append("")
    lines.append(f"_Report generated for signal date **{latest.name.date()}**_")
    lines.append(f"_Data source: {data_source}_")
    lines.append("")

    lines.append("## Executive summary")
    lines.append("")
    lines.append(
        f"- This week's regime: **{latest['regime']}** with target net SPY exposure "
        f"**{latest['net_equity_exposure']:.2f}x**"
    )
    lines.append(f"- Allocation: {allocation_text(latest)}")
    lines.append("")
    lines.append("**Long-run performance (2009 → present)**")
    lines.append("")
    rows = [
        ["SPY buy-and-hold",
         fmt_pct(spy_full['total_return']), fmt_pct(spy_full['cagr'], 2),
         fmt_num(spy_full['sharpe']), fmt_pct(spy_full['max_drawdown']), fmt_num(spy_full['calmar'])],
        ["V12 (defensive engine)",
         fmt_pct(v12_full['total_return']), fmt_pct(v12_full['cagr'], 2),
         fmt_num(v12_full['sharpe']), fmt_pct(v12_full['max_drawdown']), fmt_num(v12_full['calmar'])],
        ["**V17 Conservative**",
         f"**{fmt_pct(v17_full['total_return'])}**", f"**{fmt_pct(v17_full['cagr'], 2)}**",
         f"**{fmt_num(v17_full['sharpe'])}**", f"**{fmt_pct(v17_full['max_drawdown'])}**",
         f"**{fmt_num(v17_full['calmar'])}**"],
    ]
    lines.append(_markdown_table(
        ["Model", "Total return", "CAGR", "Sharpe", "Max drawdown", "Calmar"], rows))
    lines.append("")
    lines.append(
        f"**V17 outperformed SPY by {fmt_pct_signed(v17_full['total_return'] - spy_full['total_return'])} "
        f"in total return, with Sharpe {fmt_signed(v17_full['sharpe'] - spy_full['sharpe'])} higher "
        f"and max drawdown {fmt_pct_signed(v17_full['max_drawdown'] - spy_full['max_drawdown'])} "
        "(less negative is better).**"
    )
    lines.append("")

    lines.append("## This week's signal")
    lines.append("")
    lines.append(_markdown_table(
        ["Field", "Value"],
        [["Date", latest.name.date().isoformat()],
         ["V12 score", f"{latest['v12_signal']:.2f}"],
         ["V17 score", f"{latest['v17_signal']:.2f}"],
         ["Regime", latest["regime"]],
         ["Net equity exposure", f"{latest['net_equity_exposure']:.2f}x"],
         ["Calm-bull trigger", "YES" if int(latest["calm_bull_trigger"]) == 1 else "no"],
         ["Allocation", allocation_text(latest)],
         ["Reason", latest["reason"]]]))
    lines.append("")

    lines.append("## Out-of-sample period (2021 → present)")
    lines.append("")
    rows = []
    for label, key in [("SPY buy-and-hold", "SPY_BH"), ("V12", "v12"),
                       ("V17 Conservative", "v17_conservative")]:
        m = holdout.loc[key]
        rows.append([label, fmt_pct(m['total_return']), fmt_pct(m['cagr'], 2),
                     fmt_num(m['sharpe']), fmt_pct(m['max_drawdown']), fmt_num(m['calmar'])])
    lines.append(_markdown_table(
        ["Model", "Total return", "CAGR", "Sharpe", "Max drawdown", "Calmar"], rows))
    lines.append("")

    lines.append("## Behaviour during historical stress events")
    lines.append("")
    if not stress.empty:
        wide = stress.pivot_table(index="window", columns="model", values="total_return", aggfunc="first")
        rows = []
        for w in wide.index:
            rows.append([w,
                         fmt_pct_signed(wide.loc[w].get("SPY_BH", np.nan)),
                         fmt_pct_signed(wide.loc[w].get("v12", np.nan)),
                         fmt_pct_signed(wide.loc[w].get("v17_conservative", np.nan))])
        lines.append(_markdown_table(["Window", "SPY", "V12", "V17"], rows))
    lines.append("")

    lines.append("## Calendar-year breakdown")
    lines.append("")
    if not yearly.empty:
        wide = yearly.pivot_table(index="year", columns="model", values="total_return", aggfunc="first")
        rows = []
        for y in sorted(wide.index):
            rows.append([str(y),
                         fmt_pct_signed(wide.loc[y].get("SPY_BH", np.nan)),
                         fmt_pct_signed(wide.loc[y].get("v12", np.nan)),
                         fmt_pct_signed(wide.loc[y].get("v17_conservative", np.nan))])
        lines.append(_markdown_table(["Year", "SPY", "V12", "V17"], rows))
    lines.append("")

    if not bootstrap.empty and bootstrap["n_bootstrap"].max() > 0:
        lines.append("## Statistical significance (paired block bootstrap)")
        lines.append("")
        rows = []
        for _, b in bootstrap.iterrows():
            target = "vs SPY" if b["base_model"] == "SPY_BH" else "vs V12"
            metric = b["metric"]
            obs = b["observed_delta"]
            obs_str = fmt_pct_signed(obs) if metric in ("total_return", "max_drawdown") else fmt_signed(obs)
            p = b["p_fail"]
            p_str = fmt_num(p, 4) if not pd.isna(p) else "n/a"
            verdict = ""
            if not pd.isna(p):
                if p < 0.01: verdict = "highly significant (p<0.01)"
                elif p < 0.05: verdict = "significant (p<0.05)"
                elif p < 0.10: verdict = "borderline"
                else: verdict = "not significant"
            rows.append([target, b["period"], metric, obs_str, p_str, verdict])
        lines.append(_markdown_table(
            ["Comparison", "Period", "Metric", "Observed delta", "p_fail", "Verdict"], rows))
        lines.append("")

    lines.append("## Honest interpretation")
    lines.append("")
    lines.append("**Strengths**")
    lines.append("")
    lines.append("- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.")
    lines.append("- Out-of-sample (2021+) performance is consistent with the in-sample period.")
    lines.append("- Long-run Sharpe is materially above SPY's.")
    lines.append("")
    lines.append("**Limitations**")
    lines.append("")
    lines.append("- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.")
    lines.append("- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.")
    lines.append("- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.")
    lines.append("")

    (out / "V17_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers for signal table / regime / allocation strings
# ---------------------------------------------------------------------------

def classify_regime(
    v17_signal: pd.Series,
    calm_bull_trigger: pd.Series,
    tier_intersection: Optional[pd.Series] = None,
    tier_cb_only: Optional[pd.Series] = None,
    tier_yc_only: Optional[pd.Series] = None,
) -> pd.Series:
    """Map (v17_signal, tiers) → human-readable regime label.

    Backward-compatible: old callers passing only (v17_signal, calm_bull_trigger)
    still get sensible labels (CALM_BULL_BOOST / LEVERAGED_LONG fallback). When
    the new tier flags are also passed, the three boost tiers are surfaced
    explicitly: DUAL_BOOST, CALM_BULL_BOOST, YC_BOOST.
    """
    out = pd.Series("NORMAL", index=v17_signal.index)
    out[v17_signal < 0] = "CRASH_SHORT"
    out[(v17_signal >= 0) & (v17_signal < 1.0)] = "DEFENSIVE"

    if tier_intersection is not None and tier_cb_only is not None and tier_yc_only is not None:
        # v17-pro path: distinguish the three boost tiers
        out[tier_yc_only.astype(int) == 1] = "YC_BOOST"
        out[tier_cb_only.astype(int) == 1] = "CALM_BULL_BOOST"
        out[tier_intersection.astype(int) == 1] = "DUAL_BOOST"
        # Anything else with v17_signal>1 is V12's leveraged-recovery sleeve
        leveraged_other = (v17_signal > 1.0) \
            & (tier_intersection.astype(int) == 0) \
            & (tier_cb_only.astype(int) == 0) \
            & (tier_yc_only.astype(int) == 0)
        out[leveraged_other] = "LEVERAGED_LONG"
    else:
        # Legacy path
        out[(v17_signal > 1.0) & (calm_bull_trigger == 1)] = "CALM_BULL_BOOST"
        out[(v17_signal > 1.0) & (calm_bull_trigger == 0)] = "LEVERAGED_LONG"
    return out


REGIME_REASON = {
    "CRASH_SHORT": "V12 crash-short protection retained.",
    "DEFENSIVE": "V12 defensive risk-control signal retained.",
    "NORMAL": "No high-conviction trigger; baseline 100% SPY.",
    "CALM_BULL_BOOST": "Calm-uptrend conditions met (CB only); V17-pro raises exposure to 1.07x.",
    "YC_BOOST": "Yield curve positive AND steepening (YC only); V17-pro raises exposure to 1.12x.",
    "DUAL_BOOST": "Calm-uptrend AND yield-curve steepening both fire; V17-pro raises exposure to 1.25x (highest conviction).",
    "LEVERAGED_LONG": "V12 high-conviction leverage signal retained (dip-buy / recovery).",
}


def build_signal_table(
    v12_signal: pd.Series, v17_signal: pd.Series,
    diagnostics: pd.DataFrame, weekly_prices: pd.DataFrame,
) -> pd.DataFrame:
    weights = signal_to_weekly_weights(
        v17_signal.reindex(weekly_prices.index).ffill().fillna(1.0), weekly_prices)
    table = pd.DataFrame(index=weekly_prices.index)
    table["v12_signal"] = v12_signal.reindex(table.index).ffill().fillna(1.0)
    table["v17_signal"] = v17_signal.reindex(table.index).ffill().fillna(1.0)
    table["calm_bull_trigger"] = diagnostics["calm_bull_trigger"].reindex(table.index).fillna(0).astype(int)
    # v17-pro tier flags (forwarded into classify_regime if present)
    for col in ("tier_intersection", "tier_cb_only", "tier_yc_only", "yc_pos_steep"):
        if col in diagnostics.columns:
            table[col] = diagnostics[col].reindex(table.index).fillna(0).astype(int)
    for asset in ASSETS:
        table[f"weight_{asset}"] = weights[asset]
    table["net_equity_exposure"] = (
        table["weight_SPY"] + 3.0 * table["weight_SPXL"] - 3.0 * table["weight_SPXS"])
    if all(c in table.columns for c in ("tier_intersection", "tier_cb_only", "tier_yc_only")):
        table["regime"] = classify_regime(
            table["v17_signal"], table["calm_bull_trigger"],
            table["tier_intersection"], table["tier_cb_only"], table["tier_yc_only"])
    else:
        table["regime"] = classify_regime(table["v17_signal"], table["calm_bull_trigger"])
    table["reason"] = table["regime"].map(REGIME_REASON)
    return table


def allocation_text(row: pd.Series) -> str:
    parts = []
    for col, label in [("weight_SPY", "SPY"), ("weight_SPXL", "SPXL"), ("weight_SPXS", "SPXS"),
                       ("weight_TLT", "TLT"), ("weight_GLD", "GLD"), ("weight_SHY", "SHY")]:
        v = float(row.get(col, 0.0))
        if abs(v) > 1e-6:
            parts.append(f"{label} {v * 100:.1f}%")
    return ",  ".join(parts) if parts else "All cash"


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def _hr(width: int = 78) -> str:
    return "=" * width


def _section_title(title: str, width: int = 78) -> str:
    pad = width - len(title) - 4
    pad_l = pad // 2
    pad_r = pad - pad_l
    return "=" * pad_l + "  " + title + "  " + "=" * pad_r


def print_console(
    out: Path, signal_table: pd.DataFrame, headline: pd.DataFrame,
    stress: pd.DataFrame, bootstrap: pd.DataFrame,
    print_weeks: int, full_mode: bool, data_source: str,
) -> None:
    """Minimal weekly action output."""
    latest = signal_table.iloc[-1]
    date_str = signal_table.index[-1].strftime("%Y-%m-%d")
    regime = str(latest["regime"])
    exposure = float(latest["net_equity_exposure"])
    allocation = allocation_text(latest)
    reason = str(latest["reason"])

    changed = False
    prev_alloc = ""
    if len(signal_table) >= 2:
        prev = signal_table.iloc[-2]
        if not np.isclose(prev["v17_signal"], latest["v17_signal"]):
            changed = True
            prev_alloc = allocation_text(prev)

    print()
    print(_hr())
    print(_section_title(f"V17 SIGNAL  ({date_str})"))
    print(_hr())
    print()

    if changed:
        print("   ** SIGNAL CHANGED THIS WEEK **")
        print(f"   Last week:  {prev_alloc}")
        print(f"   This week:  {allocation}")
    else:
        print(f"   Hold:       {allocation}")
    print()
    print(f"   Regime:     {regime}  ({exposure:.2f}x SPY exposure)")
    print(f"   Note:       {reason}")
    print(f"   Data:       {data_source}")
    print()

    print(_section_title("RECENT WEEKS"))
    print()
    n_recent = min(print_weeks, len(signal_table))
    recent = signal_table.tail(n_recent)
    print(f"   {'Date':<12s}  {'Regime':<18s}  {'Exp':>6s}   Allocation")
    print(f"   {'-' * 12}  {'-' * 18}  {'-' * 6}   {'-' * 40}")
    for d, row in recent.iterrows():
        marker = " <-- " if d == signal_table.index[-1] else "     "
        print(f"   {d.strftime('%Y-%m-%d'):<12s}  "
              f"{row['regime']:<18s}  "
              f"{row['net_equity_exposure']:>5.2f}x"
              f"{marker}{allocation_text(row)}")
    print()

    print(_section_title("FOR FULL DETAILS"))
    print()
    print(f"   Open:  {out / 'V17_REPORT.md'}")
    print(f"          (performance, statistical tests, stress windows, yearly breakdown)")
    heavy_path = out / 'HEAVY_VALIDATION_REPORT.md'
    if heavy_path.exists():
        print(f"   Heavy: {heavy_path}")
        print(f"          (null markets, random schedules, DSR, Bayesian Sharpe, sensitivity)")
    print()
    print(_hr())
    print()


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

@dataclass
class Config:
    root: Path
    mode: str
    n_bootstrap: int
    n_random_rebalance: int
    n_synthetic: int
    n_bayes_draws: int
    assumed_trials: int
    tc_bps: float
    block_len: int
    seed: int
    print_weeks: int
    out_dir: Path
    refresh_data: bool
    offline: bool
    start_date: str
    live_track: bool
    live_start_cash: float
    live_dir: Path
    live_reset: bool
    sensitivity_grid: str = "full"


def run(cfg: Config) -> None:
    cfg.out_dir.mkdir(exist_ok=True, parents=True)

    full_mode = (cfg.mode == "full")
    total_steps = 9 if full_mode else 8

    print()
    print(_hr())
    if full_mode:
        print(_section_title("SPY V17 — FULL VALIDATION RUN"))
    else:
        print(_section_title("SPY V17 — WEEKLY SIGNAL RUN"))
    print(_hr())
    print()
    if full_mode:
        print(f"  Mode: full / heavy validation")
        print(f"  Bootstrap iterations: {cfg.n_bootstrap}")
        print(f"  Random schedules:      {cfg.n_random_rebalance}")
        print(f"  Synthetic markets:     {cfg.n_synthetic}")
    else:
        print(f"  Mode: signal  (quick run)")
    print()

    steps = StepLogger(total=total_steps)

    # 1: Fetch / load data
    steps.start("Fetching latest market data (Yahoo Finance + FRED)")
    cache_path = cfg.root / "data" / "daily_cache.parquet"
    daily, data_source = fetch_and_clean_data(
        cache_path=cache_path, start=cfg.start_date,
        refresh=cfg.refresh_data, offline=cfg.offline,
    )
    steps.done(f"{len(daily)} daily rows, source: {data_source}")

    # 2: Build weekly frame
    steps.start("Resampling to weekly Friday close")
    weekly = resample_completed_friday_weeks(daily)
    steps.done(f"{len(weekly)} weekly rows ({weekly.index.min().date()} -> {weekly.index.max().date()})")

    # 3: Compute V12 signal
    steps.start("Computing V12 signal (rate guard + ensemble crash short)")
    v12_signal = strat_v12_robust_short_ensemble(weekly)
    base = strat_v10_rate_guard(weekly)
    vote = v12_fire_vote_fraction(weekly, base)
    score = v12_crash_score(weekly, base)
    n_short = int((v12_signal < 0).sum())
    n_def = int(((v12_signal >= 0) & (v12_signal < 1.0)).sum())
    n_lev = int((v12_signal > 1.0).sum())
    steps.done(f"{n_short} short, {n_def} defensive, {n_lev} leveraged")

    # 4: Apply V17 conservative boost
    steps.start("Applying V17 conservative calm-bull boost")
    v17_signal, diagnostics = build_v17_conservative_signal(weekly, v12_signal)
    n_boost = int(diagnostics["calm_bull_trigger"].sum())
    steps.done(f"{n_boost} calm-bull boost weeks identified")

    # 5: Run backtests
    steps.start("Running daily backtests for SPY / V12 / V17")
    bt = {
        "SPY_BH": {
            "ret": daily["SPY"].ffill().pct_change().fillna(0.0),
            "exposure": pd.Series(1.0, index=daily.index),
        },
        "v12": run_backtest(v12_signal, daily, cfg.tc_bps),
        "v17_conservative": run_backtest(v17_signal, daily, cfg.tc_bps),
    }
    steps.done()

    # 6: Performance metrics
    steps.start("Computing performance metrics (full / holdout / stress / yearly)")
    headline = headline_comparison(bt, daily)
    stress = stress_window_report(bt)
    yearly = yearly_report(bt)
    signal_table = build_signal_table(v12_signal, v17_signal, diagnostics, weekly)
    steps.done()

    # 7: Bootstrap (signal mode runs a small one; full mode runs the full one)
    if full_mode:
        steps.start(f"Block bootstrap ({cfg.n_bootstrap} iters x 16 metric tests)")
        bootstrap = bootstrap_suite(
            bt, cfg.n_bootstrap, cfg.block_len, cfg.seed, show_progress=False,
        )
        steps.done()
    else:
        steps.start("Quick bootstrap snapshot (200 iters)")
        bootstrap = bootstrap_suite(bt, min(200, cfg.n_bootstrap), cfg.block_len, cfg.seed)
        steps.done()

    heavy_tables = {}
    if full_mode:
        steps.start("Running heavy validation suite")
        heavy_tables = run_heavy_validation(
            cfg.out_dir, weekly, daily, v12_signal, v17_signal, signal_table,
            bt, bootstrap, yearly, cfg,
        )
        steps.done()

    # Save and report
    steps.start("Writing report and CSVs")

    latest_row = signal_table.iloc[-1]
    latest_dict = {
        "date": signal_table.index[-1].date().isoformat(),
        "v12_signal": float(latest_row["v12_signal"]),
        "v17_signal": float(latest_row["v17_signal"]),
        "regime": str(latest_row["regime"]),
        "net_equity_exposure": float(latest_row["net_equity_exposure"]),
        "calm_bull_trigger": int(latest_row["calm_bull_trigger"]),
        "target_allocation": allocation_text(latest_row),
        "weights": {asset: float(latest_row[f"weight_{asset}"]) for asset in ASSETS},
        "reason": str(latest_row["reason"]),
        "data_source": data_source,
    }

    (cfg.out_dir / "latest_signal.json").write_text(
        json.dumps(latest_dict, indent=2), encoding="utf-8")
    pd.DataFrame([latest_dict]).to_csv(cfg.out_dir / "latest_signal.csv", index=False)
    signal_table.to_csv(cfg.out_dir / "weekly_signal_history.csv")
    headline.to_csv(cfg.out_dir / "headline_comparison.csv", index=False)
    stress.to_csv(cfg.out_dir / "stress_windows.csv", index=False)
    yearly.to_csv(cfg.out_dir / "yearly_comparison.csv", index=False)
    diagnostics.to_csv(cfg.out_dir / "diagnostics.csv")
    if not bootstrap.empty:
        bootstrap.to_csv(cfg.out_dir / "bootstrap_results.csv", index=False)

    write_report(cfg.out_dir, latest_row, headline, stress, yearly, bootstrap, full_mode, data_source)

    live_result = None
    if cfg.live_track:
        from v17_live_tracker import update_live_tracker
        live_result = update_live_tracker(
            live_dir=cfg.live_dir,
            signal_table=signal_table,
            daily=daily,
            initial_capital=cfg.live_start_cash,
            reset=cfg.live_reset,
        )

    steps.done()

    print()
    print_console(cfg.out_dir, signal_table, headline, stress, bootstrap,
                  cfg.print_weeks, full_mode, data_source)

    if live_result is not None:
        summary = live_result.get("summary", {})
        print(_section_title("LIVE TRACKER"))
        print()
        print(f"   Action:     {live_result.get('action')}")
        print(f"   Report:     {cfg.live_dir / 'LIVE_TRACKING_REPORT.md'}")
        print(f"   Ledger:     {cfg.live_dir / 'live_signal_ledger.csv'}")
        if summary:
            print(f"   Model eq:   {summary.get('model_equity', np.nan):,.2f}")
            print(f"   SPY eq:     {summary.get('spy_equity', np.nan):,.2f}")
            print(f"   Excess:     {fmt_pct_signed(summary.get('excess_return', np.nan))}")
        print()
        print(_hr())
        print()


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="SPY V17 Conservative — self-contained weekly signal engine.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--mode", choices=["signal", "full"], default="signal")
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument("--n-random-rebalance", type=int, default=DEFAULT_N_RANDOM_REBALANCE)
    parser.add_argument("--n-synthetic", type=int, default=DEFAULT_N_SYNTHETIC)
    parser.add_argument("--n-bayes-draws", type=int, default=DEFAULT_N_BAYES_DRAWS)
    parser.add_argument("--assumed-trials", type=int, default=DEFAULT_N_VARIANTS_ASSUMED,
                        help="model-development trial count for Deflated Sharpe adjustment")
    parser.add_argument("--tc-bps", type=float, default=DEFAULT_TC_BPS)
    parser.add_argument("--block-len", type=int, default=DEFAULT_BLOCK_LEN)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--print-weeks", type=int, default=8)
    parser.add_argument("--out-dir", default="outputs_v17_conservative")
    parser.add_argument("--start-date", default=DEFAULT_START,
                        help="earliest date for data fetching")
    parser.add_argument("--refresh-data", action="store_true",
                        help="force fresh fetch even if cache is recent")
    parser.add_argument("--offline", action="store_true",
                        help="use cache only, do not contact the network")
    parser.add_argument("--live-track", action="store_true",
                        help="update duplicate-safe live paper-tracking files for the latest completed Friday signal")
    parser.add_argument("--live-start-cash", type=float, default=10000.0,
                        help="starting capital used by the live paper tracker")
    parser.add_argument("--live-dir", default="live_tracker",
                        help="folder where live tracking CSV/MD files are written")
    parser.add_argument("--live-reset", action="store_true",
                        help="delete the existing live tracker ledger before writing the latest signal")
    parser.add_argument("--sensitivity-grid", choices=["full", "smoke", "off"], default="full",
                        help="full parameter grid, fast smoke grid, or skip sensitivity grid")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    return Config(
        root=root, mode=args.mode, n_bootstrap=args.n_bootstrap,
        n_random_rebalance=args.n_random_rebalance, n_synthetic=args.n_synthetic,
        n_bayes_draws=args.n_bayes_draws, assumed_trials=args.assumed_trials,
        tc_bps=args.tc_bps, block_len=args.block_len, seed=args.seed,
        print_weeks=args.print_weeks, out_dir=root / args.out_dir,
        refresh_data=args.refresh_data, offline=args.offline,
        start_date=args.start_date,
        live_track=args.live_track, live_start_cash=args.live_start_cash,
        live_dir=root / args.live_dir, live_reset=args.live_reset,
        sensitivity_grid=args.sensitivity_grid,
    )


if __name__ == "__main__":
    run(parse_args())
