# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-05-22 |
| Last data date | 2026-05-26 |
| Tracker action | updated_existing_signal_no_duplicate |
| Tracked weeks | 4 |
| Closed weeks | 3 |
| Pending next-week signals | 0 |
| Signal rows in ledger | 4 |
| Model equity (SGD) | 10,461.18 |
| SPY equity (SGD) | 10,428.50 |
| Model total return | 4.6% |
| SPY total return | 4.3% |
| Excess return | +0.3% |
| Model Sharpe | 5.631 |
| SPY Sharpe | 5.550 |
| Model MaxDD | -2.0% |
| SPY MaxDD | -1.9% |
| Latest target allocation | SPY 90.0%,  SPXL 10.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-08 | 2026-05-11 | ACTIVE | CALM_BULL_BOOST | 1.07 | SPY 96.5%,  SPXL 3.5% |
| 2026-05-15 | 2026-05-18 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-05-22 | 2026-05-26 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-01 | 2026-05-04 | CLOSED | CALM_BULL_BOOST | +2.5% | +2.4% | +0.2% |
| 2026-05-08 | 2026-05-11 | CLOSED | CALM_BULL_BOOST | +0.2% | +0.2% | +0.0% |
| 2026-05-15 | 2026-05-18 | CLOSED | NORMAL | +0.9% | +0.9% | +0.0% |
| 2026-05-22 | 2026-05-26 | OPEN | STRONG_CALM_BULL | +0.9% | +0.8% | +0.2% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
