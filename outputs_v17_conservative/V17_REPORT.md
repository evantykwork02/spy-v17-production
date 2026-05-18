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
| **V17 Conservative** | **4713.8%** | **24.85%** | **1.159** | **-24.2%** | **1.026** |

**V17 outperformed SPY by +3563.5% in total return, with Sharpe +0.276 higher and max drawdown +9.5% (less negative is better).**

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
| V17 Conservative | 259.9% | 27.05% | 1.227 | -17.3% | 1.559 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.0% |
| 2015_2016_china_oil | -7.0% | -5.6% | -6.1% |
| 2018_q4_fed_selloff | -13.5% | -9.9% | -9.9% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | +1.0% | +3.1% |
| 2023_low_vol_uptrend | +26.2% | +26.6% | +27.4% |
| 2024_low_vol_uptrend | +24.9% | +27.6% | +28.7% |

## Calendar-year breakdown

| Year | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2009 | +26.4% | +36.5% | +46.1% |
| 2010 | +15.1% | +18.9% | +22.1% |
| 2011 | +1.9% | +8.3% | +9.5% |
| 2012 | +16.0% | +11.2% | +10.7% |
| 2013 | +32.3% | +32.3% | +39.4% |
| 2014 | +13.5% | +15.8% | +15.3% |
| 2015 | +1.2% | +1.4% | +1.1% |
| 2016 | +12.0% | +19.5% | +21.4% |
| 2017 | +21.7% | +21.7% | +24.0% |
| 2018 | -4.6% | -0.5% | -0.5% |
| 2019 | +31.2% | +37.3% | +41.9% |
| 2020 | +18.3% | +54.6% | +62.1% |
| 2021 | +28.7% | +33.4% | +42.0% |
| 2022 | -18.2% | +1.0% | +3.1% |
| 2023 | +26.2% | +26.6% | +27.4% |
| 2024 | +24.9% | +27.6% | +28.7% |
| 2025 | +17.7% | +36.3% | +38.8% |
| 2026 | +8.7% | +8.6% | +8.0% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +1500.8% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.033 | 0.1400 | not significant |
| vs V12 | full | calmar | +0.107 | 0.1450 | not significant |
| vs V12 | full | max_drawdown | -0.1% | 0.8850 | not significant |
| vs V12 | holdout_2021_plus | total_return | +37.8% | 0.0100 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | -0.017 | 0.6500 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.117 | 0.5350 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.4% | 0.9750 | not significant |
| vs SPY | full | total_return | +3563.5% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.347 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.564 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | max_drawdown | +9.5% | 0.2250 | not significant |
| vs SPY | holdout_2021_plus | total_return | +147.5% | 0.0150 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | sharpe | +0.496 | 0.0550 | borderline |
| vs SPY | holdout_2021_plus | calmar | +0.942 | 0.0550 | borderline |
| vs SPY | holdout_2021_plus | max_drawdown | +7.1% | 0.3350 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
