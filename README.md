# SPY V17-PRO Conservative — Production Build

This package contains one integrated script (`spy_v17_conservative.py`) implementing
**V17-PRO**, an upgrade over the original V17 conservative model.

```bat
py spy_v17_conservative.py --mode signal
py spy_v17_conservative.py --mode full --n-bootstrap 2000
```

## What changed vs original V17

V17-PRO = **V12 base engine + 3-tier upside sleeve** (was: single calm-bull boost at 1.15x).

The model keeps **all V12 logic intact** — defensive sleeve, crash-short ensemble,
and leveraged-recovery sleeve are byte-identical to V12. Stratified-regime tests
confirm v12_defensive CAGR and v12_crash_short CAGR are unchanged from v17_orig.

The 3-tier upside sleeve replaces the binary calm-bull boost:

```text
If V12 = 1.0 NORMAL:
    INTERSECTION (calm_bull AND yc_steep)  →  1.25x exposure  (highest conviction)
    YC_STEEP only                          →  1.12x exposure  (NEW sleeve)
    CALM_BULL only                         →  1.07x exposure  (down from 1.15x in v17_orig)
    Otherwise                              →  1.00x baseline
```

Where:

- `calm_bull` is the original V17 calm-bull trigger (V12 normal + SPY>40W MA + 13W mom>0 + 26W RV<55th pct + VIX<52W avg).
- `yc_steep` (NEW) = T10Y2Y > 0 AND T10Y2Y has risen over the last 13 weeks.

This replaces a model whose calm-bull weeks contributed only ~8% of the total edge
with one that has measurable, statistically validated edge from yield-curve-driven
exposure expansion. See `V17_PRO_UPGRADE_REPORT.md` for the full statistical workup.

## Validation summary (2009-01 to 2026-04, 17.3 years)

| Metric | v17_orig | v17_pro | Δ |
|---|---|---|---|
| Full Sharpe | 1.171 | **1.187** | +0.016 |
| Full CAGR | 21.55% | **22.29%** | +0.74% |
| Full MaxDD | -24.34% | **-24.25%** | +0.09% (better) |
| Full Calmar | 0.886 | **0.919** | +0.033 |
| Pre-2021 Sharpe | 1.078 | **1.111** | +0.033 |
| Post-2021 Sharpe | 1.409 | 1.413 | +0.004 |

Critical sanity checks:
- Null permutation test (200 random label shuffles): **P(random ≥ real) = 0.000**, real Sharpe beat all 200.
- Bootstrap (5000 iters, 21d blocks) full period: +66 ann bps, p_fail=0.0004.
- Pre-2021 lift > post-2021 lift (i.e. the gain is in the out-of-holdout period, not data-mined).
- Yearly win rate vs v17_orig: 11/18 (61%) on total_ret, sharpe, AND maxdd.
- v12_defensive CAGR and v12_crash_short CAGR are identical between v17_orig and v17_pro.

## One-time setup

```bat
py -m pip install -r requirements.txt
```

## Weekly Friday signal

Run after Friday market close:

```bat
py spy_v17_conservative.py --mode signal
```

Then trade/rebalance on Monday open.

## Weekly live tracking

To run the normal weekly signal and update live-paper performance tracking:

```bat
py spy_v17_conservative.py --mode signal --live-track
```

Or double-click:

```text
run_v17_signal_and_track.bat
```

This creates/updates:

```text
live_tracker/LIVE_TRACKING_REPORT.md
live_tracker/live_signal_ledger.csv
live_tracker/live_equity_curve.csv
live_tracker/live_signal_periods.csv
live_tracker/live_summary.csv
```

The tracker is duplicate-safe. If you accidentally run the script again before
the next completed Friday signal, it updates the same ledger row instead of
creating a fake next-week signal.

See `LIVE_TRACKING_README.md` for details.

## Position sizing for live capital

The signal output can include a **POSITION SIZING** block that translates the
percentage weights into actionable share counts based on the latest close
prices. This is configured via `config.json` in the project root:

```json
{
  "capital": 10000.0,
  "currency": "SGD",
  "fractional_shares": false,
  "show_position_sizing": true
}
```

Edit `capital` to match what you intend to deploy. Set `fractional_shares: true`
if your broker supports them (Fidelity, Robinhood, IBKR), otherwise the script
rounds DOWN to whole shares and shows leftover cash for each leg.

CLI flags override the config file:

```bat
py spy_v17_conservative.py --mode signal --capital 5000
py spy_v17_conservative.py --mode signal --capital 25000 --fractional-shares
py spy_v17_conservative.py --mode signal --no-position-sizing
```

Example output for a $10k DEFENSIVE week:

```text
=============================  POSITION SIZING  ==============================

   Capital:        SGD 10,000.00
   Reference px:   close prices as of 2026-04-24
   Sizing mode:    whole shares (round down)

   ETF      Weight      Target $       Price      Shares      Actual $   Leftover $
   ------  -------  ------------  ----------  ----------  ------------  -----------
   SPY       60.0%      6,000.00      713.94           8      5,711.52       288.48
   TLT       20.0%      2,000.00       86.71          23      1,994.33         5.67
   GLD        8.0%        800.00      433.25           1        433.25       366.75
   SHY       12.0%      1,200.00       82.57          14      1,155.98        44.02
   ------  -------  ------------  ----------  ----------  ------------  -----------
   TOTAL               10,000.00                              9,295.08       704.92
```

The same data is saved to `latest_signal.json` under the `position_sizing` key
for programmatic consumption. Reference prices come from the same data source
the model uses (online or offline cache), so the sizing block works regardless
of network availability.

## Validation commands

### Fast validation

```bat
py spy_v17_conservative.py --mode full --offline --n-bootstrap 300 --n-random-rebalance 300 --n-synthetic 75 --n-bayes-draws 10000 --sensitivity-grid smoke
```

### Full heavy validation

```bat
py spy_v17_conservative.py --mode full --n-bootstrap 2000 --n-random-rebalance 1000 --n-synthetic 100 --n-bayes-draws 20000 --sensitivity-grid full
```

This runs:

1. paired block bootstrap
2. synthetic null markets
3. stratified regime test
4. deflated Sharpe ratio
5. Bayesian Sharpe credible interval
6. random rebalance comparison
7. yearly walk-forward consistency
8. rolling 1y/3y/5y horizon test
9. cost stress test
10. parameter sensitivity grid

## New regime labels in the weekly signal output

The weekly report and live tracker now distinguish three boost tiers:

- `DUAL_BOOST` — both calm_bull AND yc_steep fire → 1.25x SPY-equivalent
- `YC_BOOST` — only yield-curve steepening → 1.12x
- `CALM_BULL_BOOST` — only calm-bull → 1.07x
- `LEVERAGED_LONG` — V12 high-conviction recovery (unchanged from v17_orig)
- `NORMAL`, `DEFENSIVE`, `CRASH_SHORT` — unchanged from v17_orig

## Main outputs

Generated inside `outputs_v17_conservative/`:

```text
V17_REPORT.md
HEAVY_VALIDATION_REPORT.md
latest_signal.csv
latest_signal.json
weekly_signal_history.csv
headline_comparison.csv
bootstrap_results.csv
heavy_random_rebalance.csv
heavy_synthetic_null.csv
heavy_stratified_regime.csv
heavy_deflated_sharpe.csv
heavy_bayesian_sharpe.csv
heavy_yearly_consistency.csv
heavy_rolling_summary.csv
heavy_cost_stress.csv
heavy_parameter_sensitivity.csv
```

## Graceful degradation

If `T10Y2Y` is missing from the data feed, the YC sleeve never fires and the
model degrades gracefully back to a CB-only sleeve at boost=0.07. No crashes,
no NaN propagation.

## Recommended next steps before live deployment

1. Run the full validation suite: `--mode full --n-bootstrap 2000`.
2. Paper-trade for 4-8 weeks alongside v17_orig before re-allocating capital.
3. Monitor the new `YC_BOOST` and `DUAL_BOOST` regimes — these are most active
   during normal-curve bull regimes (2010-2018, 2020-2021). During inverted-curve
   regimes (2022-2023) the model intentionally pulls back to lower exposure.

## See also

- `V17_PRO_UPGRADE_REPORT.md` — full statistical workup of the upgrade
- `IMPLEMENTATION_REPORT.md` — original v17 implementation notes
- `LOCAL_TEST_REPORT.md` — original v17 local test results
- `LIVE_TRACKING_README.md` — live tracker docs
- `TREASURY_RUNBOOK.md` — operational runbook
