# SPY V17 Conservative - Deployment Audit Report

Generated: 2026-05-04 00:08:03
Overall status: **PASS**
Counts: PASS=17, WARN=0, FAIL=0

## Latest signal

- Signal date: 2026-05-01
- Regime: CALM_BULL_BOOST
- V17 signal / net exposure: 1.07x
- Allocation: SPY 96.5%,  SPXL 3.5%
- Reason: Calm-uptrend conditions met (CB only); V17-pro raises exposure to 1.07x.
- Data source: forced refresh

## Audit checks

| Category | Test | Status | Detail | Recommendation |
|---|---:|:---:|---|---|
| data | required columns present | PASS | all required columns present: SPY, SPXL, SPXS, TLT, GLD, SHY, VIX, VIX3M |  |
| data | date index monotonic | PASS | rows=4388, start=2008-11-19, end=2026-05-01 |  |
| data | duplicate dates | PASS | duplicate_dates=0 |  |
| data | positive asset prices | PASS | all asset prices are positive |  |
| data | SPY daily outlier guard | PASS | max_abs_daily_return=10.94% | Investigate source prices if >30%. |
| data | asset missing values after aligned start | PASS | missing_counts={'SPY': 0, 'SPXL': 0, 'SPXS': 0, 'TLT': 0, 'GLD': 0, 'SHY': 0} | Cache should be aligned to first valid date across all tradeable assets. |
| data | data freshness | PASS | last_data_date=2026-05-01, age_calendar_days=3 | For a real weekly run, use --refresh-data after the latest Friday close. |
| timing | no fake future Friday on midweek rerun | PASS | simulated_as_of=2026-04-29, last_weekly_label=2026-04-24 |  |
| timing | Friday signal delayed by one daily bar | PASS | changed_weeks_checked=274, failures=[] | Backtest uses next trading day's close-to-close return as a proxy; live Monday-open execution can differ from this proxy. |
| weights | weights sum and bounds | PASS | min_weight=0.000000, max_weight=1.000000, min_sum=1.000000, max_sum=1.000000 |  |
| weights | net exposure bounds | PASS | min_exposure=-1.00, max_exposure=1.70, avg_exposure=1.06 |  |
| performance | full-period CAGR > SPY | PASS | V17=23.31%, SPY=15.44% |  |
| performance | full-period Sharpe > SPY | PASS | V17=1.209, SPY=0.877 |  |
| performance | full-period max drawdown better than SPY | PASS | V17=-24.25%, SPY=-33.72% |  |
| performance | holdout Sharpe > SPY | PASS | V17=1.416, SPY=0.894 |  |
| performance | holdout max drawdown better than SPY | PASS | V17=-17.11%, SPY=-24.50% |  |
| live_tracker | duplicate-safe same-signal rerun | PASS | first_action=appended_first_signal, second_action=updated_existing_signal_no_duplicate, ledger_rows=1 |  |

## Deployment note

This audit validates mechanics and historical robustness. It does not guarantee future profit. For live testing, keep the model logic frozen, use the refreshed Friday-after-close signal, record actual fills, and compare live returns against the tracker and SPY.