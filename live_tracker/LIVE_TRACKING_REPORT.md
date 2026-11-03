# V17 Live Paper Tracker

This tracker is duplicate-safe. Rerunning during the same signal week updates reports but does **not** append a duplicate or fake future Friday signal.

## Current summary

| Field | Value |
| --- | --- |
| Start signal date | 2026-05-01 |
| Latest signal date | 2026-10-30 |
| Last data date | 2026-11-02 |
| Tracker action | updated_existing_signal_no_duplicate |
| Tracked weeks | 27 |
| Closed weeks | 26 |
| Pending next-week signals | 0 |
| Signal rows in ledger | 27 |
| Capital injected (SGD) | 200.00 |
| Net capital contributed (SGD) | 10,200.00 |
| Model equity (SGD) | 10,577.51 |
| SPY equity (SGD) | 10,693.32 |
| Model total return | 3.8% |
| SPY total return | 4.9% |
| Excess return | -1.1% |
| Model Sharpe | 0.307 |
| SPY Sharpe | 0.509 |
| Model MaxDD | -5.6% |
| SPY MaxDD | -4.5% |
| Latest target allocation | SPY 100.0% |

## Latest signal ledger rows

| Signal date | Trade date | Status | Regime | Signal | Allocation |
| --- | --- | --- | --- | --- | --- |
| 2026-09-11 | 2026-09-14 | ACTIVE | CALM_BULL_NEUTRAL | 1.00 | SPY 100.0% |
| 2026-09-18 | 2026-09-21 | ACTIVE | CALM_BULL_NEUTRAL | 1.00 | SPY 100.0% |
| 2026-09-25 | 2026-09-28 | ACTIVE | DUAL_BOOST | 1.40 | SPY 80.0%,  SPXL 20.0% |
| 2026-10-02 | 2026-10-05 | ACTIVE | DUAL_BOOST | 1.40 | SPY 80.0%,  SPXL 20.0% |
| 2026-10-09 | 2026-10-12 | ACTIVE | DUAL_BOOST | 1.40 | SPY 80.0%,  SPXL 20.0% |
| 2026-10-16 | 2026-10-19 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-10-23 | 2026-10-26 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |
| 2026-10-30 | 2026-11-02 | ACTIVE | NORMAL | 1.00 | SPY 100.0% |

## Recent signal-period results

| Signal | Trade | Status | Regime | Model | SPY | Excess |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-11 | 2026-09-14 | CLOSED | CALM_BULL_NEUTRAL | -0.1% | -0.1% | +0.0% |
| 2026-09-18 | 2026-09-21 | CLOSED | CALM_BULL_NEUTRAL | +1.3% | +1.3% | +0.0% |
| 2026-09-25 | 2026-09-28 | CLOSED | DUAL_BOOST | -0.4% | -0.2% | -0.1% |
| 2026-10-02 | 2026-10-05 | CLOSED | DUAL_BOOST | +1.6% | +1.2% | +0.4% |
| 2026-10-09 | 2026-10-12 | CLOSED | DUAL_BOOST | -2.8% | -2.0% | -0.8% |
| 2026-10-16 | 2026-10-19 | CLOSED | NORMAL | -0.4% | -0.4% | +0.0% |
| 2026-10-23 | 2026-10-26 | CLOSED | NORMAL | -0.6% | -0.6% | +0.0% |
| 2026-10-30 | 2026-11-02 | OPEN | NORMAL | -0.5% | -0.5% | +0.0% |

## Files written

- `live_signal_ledger.csv`: one row per Friday signal; duplicate-safe
- `live_equity_curve.csv`: daily model/SPY live-paper equity curve
- `live_signal_periods.csv`: return attribution by signal period
- `live_summary.csv` / `live_summary.json`: compact dashboard summary
- `current_effective_weights.csv`: currently effective tracked weights
