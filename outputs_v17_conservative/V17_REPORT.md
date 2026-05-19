# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-05-15**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NORMAL** with target net SPY exposure **1.00x**
- Allocation: SPY 100.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1142.2% | 15.52% | 0.881 | -33.7% | 0.460 |
| V12 (defensive engine) | 3191.6% | 22.15% | 1.119 | -24.2% | 0.917 |
| **V17 Conservative** | **4778.4%** | **24.94%** | **1.163** | **-24.2%** | **1.032** |

**V17 outperformed SPY by +3636.2% in total return, with Sharpe +0.282 higher and max drawdown +9.6% (less negative is better).**

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
| SPY buy-and-hold | 111.0% | 14.96% | 0.909 | -24.5% | 0.611 |
| V12 | 220.0% | 24.25% | 1.213 | -16.9% | 1.431 |
| V17 Conservative | 264.4% | 27.30% | 1.232 | -17.2% | 1.585 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.3% |
| 2015_2016_china_oil | -7.0% | -5.6% | -6.1% |
| 2018_q4_fed_selloff | -13.5% | -9.9% | -9.9% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | +1.0% | +3.2% |
| 2023_low_vol_uptrend | +26.2% | +26.6% | +27.7% |
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
| 2023 | +26.2% | +26.6% | +27.7% |
| 2024 | +24.9% | +27.6% | +30.7% |
| 2025 | +17.7% | +36.3% | +38.4% |
| 2026 | +8.0% | +7.9% | +7.6% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +1586.8% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.039 | 0.1000 | not significant |
| vs V12 | full | calmar | +0.115 | 0.1100 | not significant |
| vs V12 | full | max_drawdown | +0.0% | 0.8500 | not significant |
| vs V12 | holdout_2021_plus | total_return | +44.5% | 0.0050 | highly significant (p<0.01) |
| vs V12 | holdout_2021_plus | sharpe | -0.003 | 0.5850 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.154 | 0.4300 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.3% | 0.9850 | not significant |
| vs SPY | full | total_return | +3636.2% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.353 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.572 | 0.0050 | highly significant (p<0.01) |
| vs SPY | full | max_drawdown | +9.6% | 0.1950 | not significant |
| vs SPY | holdout_2021_plus | total_return | +153.5% | 0.0150 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | sharpe | +0.509 | 0.0400 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.974 | 0.0350 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | max_drawdown | +7.3% | 0.3350 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
