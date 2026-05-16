# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-05-15 |
| Last data date | 2026-05-15 |
| Tracker action | updated_existing_signal_no_duplicate |
| Ledger rows | 3 |
| Initial capital (USD) | 7,811.28 |
| Model equity | 8,024.97 |
| SPY equity | 8,012.02 |
| Model total return | 2.7% |
| SPY total return | 2.6% |
| Excess return | +0.2% |
| Model Sharpe | 5.040 |
| SPY Sharpe | 5.068 |
| Model MaxDD | -1.3% |
| SPY MaxDD | -1.2% |
| Latest target allocation | SPY 100.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-08 | 2026-05-11 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-15 | pending | PENDING_EXECUTION | NORMAL | 1.00 | SPY 100.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | CLOSED | CALM_BULL_BOOST | +2.5% | +2.4% | +0.2% |
| 2026-05-08 | 2026-05-11 | OPEN | CALM_BULL_BOOST | +0.2% | +0.2% | +0.0% |
| 2026-05-15 | pending | PENDING_EXECUTION | NORMAL | n/a | n/a | n/a |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
