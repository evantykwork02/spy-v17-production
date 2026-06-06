# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-06-05 |
| Last data date | 2026-06-05 |
| Tracker action | updated_existing_signal_no_duplicate |
| Tracked weeks | 5 |
| Closed weeks | 4 |
| Pending next-week signals | 1 |
| Signal rows in ledger | 6 |
| Model equity (SGD) | 10,223.69 |
| SPY equity (SGD) | 10,234.51 |
| Model total return | 2.2% |
| SPY total return | 2.3% |
| Excess return | -0.1% |
| Model Sharpe | 1.309 |
| SPY Sharpe | 1.552 |
| Model MaxDD | -3.5% |
| SPY MaxDD | -2.9% |
| Latest target allocation | SPY 85.0%,  SPXL 15.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-08 | 2026-05-11 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-15 | 2026-05-18 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-05-22 | 2026-05-26 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |
| 2026-05-29 | 2026-06-01 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |
| 2026-06-05 | pending | PENDING_EXECUTION | NERVOUS_MARKET | 1.30 | SPY 85.0%,  SPXL 15.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | CLOSED | CALM_BULL_BOOST | +2.5% | +2.4% | +0.2% |
| 2026-05-08 | 2026-05-11 | CLOSED | CALM_BULL_BOOST | +0.2% | +0.2% | +0.0% |
| 2026-05-15 | 2026-05-18 | CLOSED | NORMAL | +0.9% | +0.9% | +0.0% |
| 2026-05-22 | 2026-05-26 | CLOSED | STRONG_CALM_BULL | +1.7% | +1.5% | +0.3% |
| 2026-05-29 | 2026-06-01 | OPEN | STRONG_CALM_BULL | -3.0% | -2.5% | -0.5% |

## Pending next signal

| Signal | Trade | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- |
| 2026-06-05 | pending | NERVOUS_MARKET | 1.3 | SPY 85.0%,  SPXL 15.0% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
