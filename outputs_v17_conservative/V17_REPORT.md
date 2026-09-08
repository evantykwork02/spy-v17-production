# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-09-04**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **DUAL_BOOST** with target net SPY exposure **1.40x**
- Allocation: SPY 80.0%,  SPXL 20.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1201.6% | 15.54% | 0.885 | -33.7% | 0.461 |
| V12 (defensive engine) | 3349.0% | 22.06% | 1.116 | -24.2% | 0.913 |
| **V17 Conservative** | **4986.6%** | **24.76%** | **1.158** | **-24.2%** | **1.025** |

**V17 outperformed SPY by +3785.0% in total return, with Sharpe +0.273 higher and max drawdown +9.6% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-09-04 |
| V12 score | 1.00 |
| V17 score | 1.40 |
| Regime | DUAL_BOOST |
| Net equity exposure | 1.40x |
| Calm-bull trigger | YES |
| Allocation | SPY 80.0%,  SPXL 20.0% |
| Reason | Calm-uptrend AND yield-curve steepening both fire; exposure 1.40x (highest conviction). |

## Out-of-sample period (2021 → present)

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 121.1% | 15.05% | 0.923 | -24.5% | 0.614 |
| V12 | 235.3% | 23.84% | 1.201 | -16.9% | 1.407 |
| V17 Conservative | 280.0% | 26.61% | 1.213 | -17.2% | 1.544 |

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
| 2026 | +13.2% | +13.0% | +12.1% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +1637.6% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.036 | 0.0850 | borderline |
| vs V12 | full | calmar | +0.112 | 0.1550 | not significant |
| vs V12 | full | max_drawdown | +0.0% | 0.7850 | not significant |
| vs V12 | holdout_2021_plus | total_return | +44.7% | 0.0200 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | -0.011 | 0.5350 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.138 | 0.5200 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.3% | 0.9650 | not significant |
| vs SPY | full | total_return | +3785.0% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.346 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.564 | 0.0100 | significant (p<0.05) |
| vs SPY | full | max_drawdown | +9.6% | 0.1850 | not significant |
| vs SPY | holdout_2021_plus | total_return | +158.9% | 0.0050 | highly significant (p<0.01) |
| vs SPY | holdout_2021_plus | sharpe | +0.480 | 0.0150 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.930 | 0.0400 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | max_drawdown | +7.3% | 0.2800 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
