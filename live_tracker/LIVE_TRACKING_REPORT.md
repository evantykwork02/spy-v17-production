# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-05-22 |
| Last data date | 2026-05-22 |
| Tracker action | updated_existing_signal_no_duplicate |
| Tracked weeks | 3 |
| Closed weeks | 2 |
| Pending next-week signals | 1 |
| Signal rows in ledger | 4 |
| Model equity | 10,363.49 |
| SPY equity | 10,346.77 |
| Model total return | 3.6% |
| SPY total return | 3.5% |
| Excess return | +0.2% |
| Model Sharpe | 4.685 |
| SPY Sharpe | 4.702 |
| Model MaxDD | -2.0% |
| SPY MaxDD | -1.9% |
| Latest target allocation | SPY 90.0%,  SPXL 10.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-08 | 2026-05-11 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-15 | 2026-05-18 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-05-22 | pending | PENDING_EXECUTION | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | CLOSED | CALM_BULL_BOOST | +2.5% | +2.4% | +0.2% |
| 2026-05-08 | 2026-05-11 | CLOSED | CALM_BULL_BOOST | +0.2% | +0.2% | +0.0% |
| 2026-05-15 | 2026-05-18 | OPEN | NORMAL | +0.9% | +0.9% | +0.0% |

## Pending next signal

| Signal | Trade | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- |
| 2026-05-22 | pending | STRONG_CALM_BULL | 1.2 | SPY 90.0%,  SPXL 10.0% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
