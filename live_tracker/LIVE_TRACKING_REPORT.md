# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-07-03 |
| Last data date | 2026-07-02 |
| Tracker action | updated_existing_signal_no_duplicate |
| Tracked weeks | 9 |
| Closed weeks | 8 |
| Pending next-week signals | 1 |
| Signal rows in ledger | 10 |
| Capital injected (SGD) | 200.00 |
| Net capital contributed (SGD) | 10,200.00 |
| Model equity (SGD) | 10,526.28 |
| SPY equity (SGD) | 10,563.01 |
| Model total return | 3.3% |
| SPY total return | 3.6% |
| Excess return | -0.4% |
| Model Sharpe | 0.987 |
| SPY Sharpe | 1.272 |
| Model MaxDD | -5.6% |
| SPY MaxDD | -4.5% |
| Latest target allocation | SPY 90.0%,  SPXL 10.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-05-15 | 2026-05-18 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-05-22 | 2026-05-26 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |
| 2026-05-29 | 2026-06-01 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |
| 2026-06-05 | 2026-06-08 | ACTIVE | NERVOUS_MARKET | 1.30 | SPY 85.0%,  SPXL 15.0% |
| 2026-06-12 | 2026-06-15 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |
| 2026-06-19 | 2026-06-22 | ACTIVE | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |
| 2026-06-26 | 2026-06-29 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-07-03 | pending | PENDING_EXECUTION | STRONG_CALM_BULL | 1.20 | SPY 90.0%,  SPXL 10.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-08 | 2026-05-11 | CLOSED | CALM_BULL_BOOST | +0.2% | +0.2% | +0.0% |
| 2026-05-15 | 2026-05-18 | CLOSED | NORMAL | +0.9% | +0.9% | +0.0% |
| 2026-05-22 | 2026-05-26 | CLOSED | STRONG_CALM_BULL | +1.7% | +1.5% | +0.3% |
| 2026-05-29 | 2026-06-01 | CLOSED | STRONG_CALM_BULL | -3.0% | -2.5% | -0.5% |
| 2026-06-05 | 2026-06-08 | CLOSED | NERVOUS_MARKET | +0.7% | +0.6% | +0.1% |
| 2026-06-12 | 2026-06-15 | CLOSED | STRONG_CALM_BULL | +1.1% | +0.9% | +0.2% |
| 2026-06-19 | 2026-06-22 | CLOSED | STRONG_CALM_BULL | -2.9% | -2.4% | -0.5% |
| 2026-06-26 | 2026-06-29 | OPEN | NORMAL | +2.2% | +2.2% | +0.0% |

## Pending next signal

| Signal | Trade | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- |
| 2026-07-03 | pending | STRONG_CALM_BULL | 1.2 | SPY 90.0%,  SPXL 10.0% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
