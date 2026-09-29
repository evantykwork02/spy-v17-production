# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-09-25 |
| Last data date | 2026-09-29 |
| Tracker action | updated_existing_signal_no_duplicate |
| Tracked weeks | 22 |
| Closed weeks | 21 |
| Pending next-week signals | 0 |
| Signal rows in ledger | 22 |
| Capital injected (SGD) | 200.00 |
| Net capital contributed (SGD) | 10,200.00 |
| Model equity (SGD) | 10,773.90 |
| SPY equity (SGD) | 10,871.61 |
| Model total return | 5.7% |
| SPY total return | 6.6% |
| Excess return | -1.0% |
| Model Sharpe | 0.739 |
| SPY Sharpe | 1.002 |
| Model MaxDD | -5.6% |
| SPY MaxDD | -4.5% |
| Latest target allocation | SPY 80.0%,  SPXL 20.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-08-07 | 2026-08-10 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-08-14 | 2026-08-17 | ACTIVE | YC_BOOST | 1.22 | SPY 89.0%,  SPXL 11.0% |
| 2026-08-21 | 2026-08-24 | ACTIVE | YC_BOOST | 1.22 | SPY 89.0%,  SPXL 11.0% |
| 2026-08-28 | 2026-08-31 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-09-04 | 2026-09-08 | ACTIVE | DUAL_BOOST | 1.40 | SPY 80.0%,  SPXL 20.0% |
| 2026-09-11 | 2026-09-14 | ACTIVE | CALM_BULL_NEUTRAL | 1.00 | SPY 100.0% |
| 2026-09-18 | 2026-09-21 | ACTIVE | CALM_BULL_NEUTRAL | 1.00 | SPY 100.0% |
| 2026-09-25 | 2026-09-28 | ACTIVE | DUAL_BOOST | 1.40 | SPY 80.0%,  SPXL 20.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-08-07 | 2026-08-10 | CLOSED | NORMAL | +0.4% | +0.4% | +0.0% |
| 2026-08-14 | 2026-08-17 | CLOSED | YC_BOOST | -1.7% | -1.4% | -0.3% |
| 2026-08-21 | 2026-08-24 | CLOSED | YC_BOOST | +0.6% | +0.5% | +0.1% |
| 2026-08-28 | 2026-08-31 | CLOSED | NORMAL | +0.1% | +0.1% | +0.0% |
| 2026-09-04 | 2026-09-08 | CLOSED | DUAL_BOOST | -1.1% | -0.8% | -0.4% |
| 2026-09-11 | 2026-09-14 | CLOSED | CALM_BULL_NEUTRAL | -0.1% | -0.1% | +0.0% |
| 2026-09-18 | 2026-09-21 | CLOSED | CALM_BULL_NEUTRAL | +1.3% | +1.3% | +0.0% |
| 2026-09-25 | 2026-09-28 | OPEN | DUAL_BOOST | -1.2% | -0.9% | -0.4% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
