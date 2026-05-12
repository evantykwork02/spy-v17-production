# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-05-08 |
| Last data date | 2026-05-12 |
| Tracker action | updated_existing_signal_no_duplicate |
| Ledger rows | 2 |
| Initial capital (USD) | 7,859.97 |
| Model equity | 8,043.48 |
| SPY equity | 8,031.86 |
| Model total return | 2.3% |
| SPY total return | 2.2% |
| Excess return | +0.1% |
| Model Sharpe | 6.504 |
| SPY Sharpe | 6.510 |
| Model MaxDD | -0.4% |
| SPY MaxDD | -0.4% |
| Latest target allocation | SPY 96.5%,  SPXL 3.5% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-08 | 2026-05-11 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | CLOSED | CALM_BULL_BOOST | +2.5% | +2.4% | +0.2% |
| 2026-05-08 | 2026-05-11 | OPEN | CALM_BULL_BOOST | -0.2% | -0.2% | -0.0% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
