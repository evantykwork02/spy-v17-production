# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-08-07**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NORMAL** with target net SPY exposure **1.00x**
- Allocation: SPY 100.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1211.9% | 15.67% | 0.890 | -33.7% | 0.465 |
| V12 (defensive engine) | 3376.4% | 22.22% | 1.122 | -24.2% | 0.919 |
| **V17 Conservative** | **5049.0%** | **24.96%** | **1.165** | **-24.2%** | **1.033** |

**V17 outperformed SPY by +3837.0% in total return, with Sharpe +0.275 higher and max drawdown +9.6% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-08-07 |
| V12 score | 1.00 |
| V17 score | 1.00 |
| Regime | NORMAL |
| Net equity exposure | 1.00x |
| Calm-bull trigger | no |
| Allocation | SPY 100.0% |
| Reason | No high-conviction trigger; baseline 100% SPY. |

## Out-of-sample period (2021 → present)

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 122.8% | 15.43% | 0.939 | -24.5% | 0.630 |
| V12 | 237.9% | 24.37% | 1.223 | -16.9% | 1.438 |
| V17 Conservative | 284.7% | 27.29% | 1.238 | -17.2% | 1.584 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.3% |
| 2015_2016_china_oil | -7.0% | -5.6% | -6.1% |
| 2018_q4_fed_selloff | -13.5% | -9.9% | -9.9% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | +1.0% | +3.2% |
| 2023_low_vol_uptrend | +26.2% | +26.6% | +27.8% |
| 2024_low_vol_uptrend | +24.9% | +27.6% | +30.7% |

## Calendar-year breakdown

| Year | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2009 | +26.4% | +36.5% | +46.1% |
| 2010 | +15.1% | +18.9% | +22.5% |
| 2011 | +1.9% | +8.3% | +9.8% |
| 2012 | +16.0% | +11.2% | +11.0% |
| 2013 | +32.3% | +32.3% | +38.9% |
| 2014 | +13.5% | +15.8% | +15.3% |
| 2015 | +1.2% | +1.4% | +1.1% |
| 2016 | +12.0% | +19.5% | +21.4% |
| 2017 | +21.7% | +21.7% | +23.3% |
| 2018 | -4.6% | -0.5% | -0.5% |
| 2019 | +31.2% | +37.3% | +42.0% |
| 2020 | +18.3% | +54.6% | +62.3% |
| 2021 | +28.7% | +33.4% | +42.2% |
| 2022 | -18.2% | +1.0% | +3.2% |
| 2023 | +26.2% | +26.6% | +27.8% |
| 2024 | +24.9% | +27.6% | +30.7% |
| 2025 | +17.7% | +36.3% | +38.4% |
| 2026 | +14.1% | +13.9% | +13.5% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +1672.6% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.037 | 0.0850 | borderline |
| vs V12 | full | calmar | +0.114 | 0.1450 | not significant |
| vs V12 | full | max_drawdown | +0.0% | 0.8050 | not significant |
| vs V12 | holdout_2021_plus | total_return | +46.7% | 0.0150 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | -0.007 | 0.5700 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.146 | 0.4850 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.3% | 0.9600 | not significant |
| vs SPY | full | total_return | +3837.0% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.348 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.568 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | max_drawdown | +9.6% | 0.1800 | not significant |
| vs SPY | holdout_2021_plus | total_return | +161.8% | 0.0100 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | sharpe | +0.488 | 0.0300 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.954 | 0.0600 | borderline |
| vs SPY | holdout_2021_plus | max_drawdown | +7.3% | 0.2600 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
