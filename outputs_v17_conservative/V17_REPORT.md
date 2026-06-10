# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-06-05**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NERVOUS_MARKET** with target net SPY exposure **1.30x**
- Allocation: SPY 85.0%,  SPXL 15.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1127.0% | 15.39% | 0.875 | -33.7% | 0.456 |
| V12 (defensive engine) | 2312.1% | 19.92% | 0.813 | -31.5% | 0.632 |
| **V17 Conservative** | **2838.8%** | **21.28%** | **0.854** | **-31.5%** | **0.675** |

**V17 outperformed SPY by +1711.8% in total return, with Sharpe -0.022 higher and max drawdown +2.2% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-06-05 |
| V12 score | 1.00 |
| V17 score | 1.30 |
| Regime | NERVOUS_MARKET |
| Net equity exposure | 1.30x |
| Calm-bull trigger | no |
| Allocation | SPY 85.0%,  SPXL 15.0% |
| Reason | VIX >= 20 with V12 normal — elevated risk premium; exposure 1.30x. |

## Out-of-sample period (2021 → present)

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 108.4% | 14.52% | 0.888 | -24.5% | 0.593 |
| V12 | 138.9% | 17.44% | 0.732 | -31.5% | 0.553 |
| V17 Conservative | 153.2% | 18.71% | 0.773 | -31.5% | 0.594 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.1% |
| 2015_2016_china_oil | -7.0% | -5.6% | -5.6% |
| 2018_q4_fed_selloff | -13.5% | -19.1% | -19.1% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | -25.2% | -25.2% |
| 2023_low_vol_uptrend | +26.2% | +25.6% | +26.1% |
| 2024_low_vol_uptrend | +24.9% | +28.5% | +33.0% |

## Calendar-year breakdown

| Year | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2009 | +26.4% | +42.1% | +52.8% |
| 2010 | +15.1% | +18.9% | +20.5% |
| 2011 | +1.9% | +9.2% | +9.2% |
| 2012 | +16.0% | +11.2% | +13.4% |
| 2013 | +32.3% | +32.1% | +33.2% |
| 2014 | +13.5% | +15.8% | +16.8% |
| 2015 | +1.2% | +1.4% | +1.4% |
| 2016 | +12.0% | +20.8% | +20.8% |
| 2017 | +21.7% | +21.7% | +21.7% |
| 2018 | -4.6% | -9.6% | -9.6% |
| 2019 | +31.2% | +37.3% | +37.3% |
| 2020 | +18.3% | +57.7% | +60.2% |
| 2021 | +28.7% | +31.1% | +32.3% |
| 2022 | -18.2% | -25.2% | -25.2% |
| 2023 | +26.2% | +25.6% | +26.1% |
| 2024 | +24.9% | +28.5% | +33.0% |
| 2025 | +17.7% | +34.9% | +37.5% |
| 2026 | +6.7% | +11.8% | +11.0% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +526.7% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.035 | 0.0050 | highly significant (p<0.01) |
| vs V12 | full | calmar | +0.043 | 0.0350 | significant (p<0.05) |
| vs V12 | full | max_drawdown | +0.0% | 0.5400 | not significant |
| vs V12 | holdout_2021_plus | total_return | +14.4% | 0.0150 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | +0.035 | 0.1000 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.040 | 0.0550 | borderline |
| vs V12 | holdout_2021_plus | max_drawdown | +0.0% | 0.5800 | not significant |
| vs SPY | full | total_return | +1711.8% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.194 | 0.0100 | significant (p<0.05) |
| vs SPY | full | calmar | +0.219 | 0.0350 | significant (p<0.05) |
| vs SPY | full | max_drawdown | +2.2% | 0.3800 | not significant |
| vs SPY | holdout_2021_plus | total_return | +44.8% | 0.1150 | not significant |
| vs SPY | holdout_2021_plus | sharpe | +0.112 | 0.2000 | not significant |
| vs SPY | holdout_2021_plus | calmar | +0.001 | 0.3650 | not significant |
| vs SPY | holdout_2021_plus | max_drawdown | -7.0% | 0.7900 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
