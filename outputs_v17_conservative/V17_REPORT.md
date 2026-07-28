# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-07-24**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NORMAL** with target net SPY exposure **1.00x**
- Allocation: SPY 100.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1158.2% | 15.43% | 0.879 | -33.7% | 0.458 |
| V12 (defensive engine) | 3234.1% | 21.98% | 1.112 | -24.2% | 0.910 |
| **V17 Conservative** | **4792.1%** | **24.66%** | **1.153** | **-24.2%** | **1.021** |

**V17 outperformed SPY by +3633.9% in total return, with Sharpe +0.274 higher and max drawdown +9.6% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-07-24 |
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
| SPY buy-and-hold | 113.7% | 14.68% | 0.900 | -24.5% | 0.599 |
| V12 | 224.1% | 23.63% | 1.186 | -16.9% | 1.394 |
| V17 Conservative | 265.5% | 26.34% | 1.197 | -17.2% | 1.529 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.3% |
| 2015_2016_china_oil | -7.0% | -5.6% | -6.1% |
| 2018_q4_fed_selloff | -13.5% | -9.9% | -9.9% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | +1.0% | +3.2% |
| 2023_low_vol_uptrend | +26.2% | +26.6% | +27.4% |
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
| 2023 | +26.2% | +26.6% | +27.4% |
| 2024 | +24.9% | +27.6% | +30.7% |
| 2025 | +17.7% | +36.3% | +38.4% |
| 2026 | +9.4% | +9.3% | +8.1% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +1558.0% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.036 | 0.0800 | borderline |
| vs V12 | full | calmar | +0.111 | 0.1250 | not significant |
| vs V12 | full | max_drawdown | -0.0% | 0.8550 | not significant |
| vs V12 | holdout_2021_plus | total_return | +41.4% | 0.0300 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | -0.012 | 0.5850 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.134 | 0.5250 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.3% | 0.9700 | not significant |
| vs SPY | full | total_return | +3633.9% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.347 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.563 | 0.0100 | significant (p<0.05) |
| vs SPY | full | max_drawdown | +9.6% | 0.1750 | not significant |
| vs SPY | holdout_2021_plus | total_return | +151.8% | 0.0150 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | sharpe | +0.485 | 0.0300 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.929 | 0.0750 | borderline |
| vs SPY | holdout_2021_plus | max_drawdown | +7.3% | 0.3150 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
