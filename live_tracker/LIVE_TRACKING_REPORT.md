# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-09-04 |
| Last data date | 2026-09-04 |
| Tracker action | appended_new_signal |
| Tracked weeks | 18 |
| Closed weeks | 17 |
| Pending next-week signals | 1 |
| Signal rows in ledger | 19 |
| Capital injected (SGD) | 200.00 |
| Net capital contributed (SGD) | 10,200.00 |
| Model equity (SGD) | 10,903.33 |
| SPY equity (SGD) | 10,923.39 |
| Model total return | 7.0% |
| SPY total return | 7.1% |
| Excess return | -0.2% |
| Model Sharpe | 1.130 |
| SPY Sharpe | 1.316 |
| Model MaxDD | -5.6% |
| SPY MaxDD | -4.5% |
| Latest target allocation | SPY 80.0%,  SPXL 20.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-07-17 | 2026-07-20 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-07-24 | 2026-07-27 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-07-31 | 2026-08-03 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |
| 2026-08-07 | 2026-08-10 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-08-14 | 2026-08-17 | ACTIVE | YC_BOOST | 1.22 | SPY 89.0%,  SPXL 11.0% |
| 2026-08-21 | 2026-08-24 | ACTIVE | YC_BOOST | 1.22 | SPY 89.0%,  SPXL 11.0% |
| 2026-08-28 | 2026-08-31 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-09-04 | pending | PENDING_EXECUTION | DUAL_BOOST | 1.40 | SPY 80.0%,  SPXL 20.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07-10 | 2026-07-13 | CLOSED | STRONG_CALM_BULL | -1.9% | -1.5% | -0.3% |
| 2026-07-17 | 2026-07-20 | CLOSED | NORMAL | -0.6% | -0.6% | +0.0% |
| 2026-07-24 | 2026-07-27 | CLOSED | NORMAL | +1.1% | +1.1% | +0.0% |
| 2026-07-31 | 2026-08-03 | CLOSED | STRONG_CALM_BULL | +4.2% | +3.5% | +0.7% |
| 2026-08-07 | 2026-08-10 | CLOSED | NORMAL | +0.4% | +0.4% | +0.0% |
| 2026-08-14 | 2026-08-17 | CLOSED | YC_BOOST | -1.7% | -1.4% | -0.3% |
| 2026-08-21 | 2026-08-24 | CLOSED | YC_BOOST | +0.6% | +0.5% | +0.1% |
| 2026-08-28 | 2026-08-31 | OPEN | NORMAL | +0.1% | +0.1% | +0.0% |

## Pending next signal

| Signal | Trade | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- |
| 2026-09-04 | pending | DUAL_BOOST | 1.4 | SPY 80.0%,  SPXL 20.0% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
