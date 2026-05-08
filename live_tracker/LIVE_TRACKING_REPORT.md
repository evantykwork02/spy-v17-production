# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-05-08 |
| Last data date | 2026-05-08 |
| Tracker action | appended_new_signal |
| Ledger rows | 2 |
| Initial capital (USD) | 7,891.48 |
| Model equity | 8,086.45 |
| SPY equity | 8,074.13 |
| Model total return | 2.5% |
| SPY total return | 2.3% |
| Excess return | +0.2% |
| Model Sharpe | 8.542 |
| SPY Sharpe | 8.564 |
| Model MaxDD | -0.4% |
| SPY MaxDD | -0.4% |
| Latest target allocation | SPY 96.5%,  SPXL 3.5% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-08 | pending | PENDING_EXECUTION | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | OPEN | CALM_BULL_BOOST | +2.5% | +2.3% | +0.2% |
| 2026-05-08 | pending | PENDING_EXECUTION | CALM_BULL_BOOST | n/a | n/a | n/a |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
