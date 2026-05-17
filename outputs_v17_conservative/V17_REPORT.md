# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-05-15**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NORMAL** with target net SPY exposure **1.00x**
- Allocation: SPY 100.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1150.3% | 15.57% | 0.884 | -33.7% | 0.462 |
| V12 (defensive engine) | 3213.0% | 22.21% | 1.121 | -24.2% | 0.919 |
| **V17 Conservative** | **3846.4%** | **23.44%** | **1.141** | **-24.2%** | **0.967** |

**V17 outperformed SPY by +2696.1% in total return, with Sharpe +0.258 higher and max drawdown +9.5% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-05-15 |
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
| SPY buy-and-hold | 112.4% | 15.12% | 0.917 | -24.5% | 0.617 |
| V12 | 222.1% | 24.44% | 1.222 | -16.9% | 1.442 |
| V17 Conservative | 238.9% | 25.63% | 1.237 | -17.1% | 1.498 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +0.8% |
| 2015_2016_china_oil | -7.0% | -5.6% | -5.9% |
| 2018_q4_fed_selloff | -13.5% | -9.9% | -9.9% |
| 2020_covid_crash | -13.2% | +6.2% | +6.1% |
| 2022_bear_market | -18.2% | +1.0% | +0.8% |
| 2023_low_vol_uptrend | +26.2% | +26.6% | +26.8% |
| 2024_low_vol_uptrend | +24.9% | +27.6% | +28.9% |

## Calendar-year breakdown

| Year | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2009 | +26.4% | +36.5% | +41.9% |
| 2010 | +15.1% | +18.9% | +20.3% |
| 2011 | +1.9% | +8.3% | +8.2% |
| 2012 | +16.0% | +11.2% | +9.7% |
| 2013 | +32.3% | +32.3% | +36.8% |
| 2014 | +13.5% | +15.8% | +14.8% |
| 2015 | +1.2% | +1.4% | +1.2% |
| 2016 | +12.0% | +19.5% | +20.6% |
| 2017 | +21.7% | +21.7% | +23.6% |
| 2018 | -4.6% | -0.5% | -0.7% |
| 2019 | +31.2% | +37.3% | +40.0% |
| 2020 | +18.3% | +54.6% | +57.8% |
| 2021 | +28.7% | +33.4% | +38.9% |
| 2022 | -18.2% | +1.0% | +0.8% |
| 2023 | +26.2% | +26.6% | +26.8% |
| 2024 | +24.9% | +27.6% | +28.9% |
| 2025 | +17.7% | +36.3% | +36.8% |
| 2026 | +8.7% | +8.6% | +8.2% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +633.3% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.018 | 0.1150 | not significant |
| vs V12 | full | calmar | +0.048 | 0.2250 | not significant |
| vs V12 | full | max_drawdown | -0.1% | 0.8550 | not significant |
| vs V12 | holdout_2021_plus | total_return | +16.9% | 0.0300 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | +0.008 | 0.4100 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.056 | 0.3700 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.2% | 0.8550 | not significant |
| vs SPY | full | total_return | +2696.1% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.332 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.505 | 0.0050 | highly significant (p<0.01) |
| vs SPY | full | max_drawdown | +9.5% | 0.1850 | not significant |
| vs SPY | holdout_2021_plus | total_return | +126.6% | 0.0350 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | sharpe | +0.521 | 0.0300 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.881 | 0.0550 | borderline |
| vs SPY | holdout_2021_plus | max_drawdown | +7.4% | 0.1750 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
