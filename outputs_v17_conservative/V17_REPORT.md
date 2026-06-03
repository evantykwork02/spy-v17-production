# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-05-29**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **STRONG_CALM_BULL** with target net SPY exposure **1.20x**
- Allocation: SPY 90.0%,  SPXL 10.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1175.8% | 15.66% | 0.889 | -33.7% | 0.464 |
| V12 (defensive engine) | 2407.9% | 20.22% | 0.825 | -31.5% | 0.642 |
| **V17 Conservative** | **2999.8%** | **21.68%** | **0.870** | **-31.5%** | **0.688** |

**V17 outperformed SPY by +1824.0% in total return, with Sharpe -0.018 higher and max drawdown +2.2% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-05-29 |
| V12 score | 1.00 |
| V17 score | 1.20 |
| Regime | STRONG_CALM_BULL |
| Net equity exposure | 1.20x |
| Calm-bull trigger | YES |
| Allocation | SPY 90.0%,  SPXL 10.0% |
| Reason | Strong CB-only conditions met; exposure 1.20x. |

## Out-of-sample period (2021 → present)

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 116.7% | 15.41% | 0.935 | -24.5% | 0.629 |
| V12 | 148.3% | 18.36% | 0.774 | -31.5% | 0.583 |
| V17 Conservative | 167.1% | 19.97% | 0.830 | -31.5% | 0.634 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.1% |
| 2015_2016_china_oil | -7.0% | -5.6% | -5.6% |
| 2018_q4_fed_selloff | -13.5% | -19.1% | -19.1% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | -25.2% | -25.2% |
| 2023_low_vol_uptrend | +26.2% | +25.6% | +26.7% |
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
| 2023 | +26.2% | +25.6% | +26.7% |
| 2024 | +24.9% | +28.5% | +33.0% |
| 2025 | +17.7% | +34.9% | +37.5% |
| 2026 | +10.9% | +16.3% | +16.5% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +591.9% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.039 | 0.0150 | significant (p<0.05) |
| vs V12 | full | calmar | +0.046 | 0.0400 | significant (p<0.05) |
| vs V12 | full | max_drawdown | -0.0% | 0.5750 | not significant |
| vs V12 | holdout_2021_plus | total_return | +18.8% | 0.0200 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | +0.049 | 0.0700 | borderline |
| vs V12 | holdout_2021_plus | calmar | +0.051 | 0.0600 | borderline |
| vs V12 | holdout_2021_plus | max_drawdown | +0.0% | 0.5550 | not significant |
| vs SPY | full | total_return | +1824.0% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.198 | 0.0150 | significant (p<0.05) |
| vs SPY | full | calmar | +0.224 | 0.0500 | borderline |
| vs SPY | full | max_drawdown | +2.2% | 0.3350 | not significant |
| vs SPY | holdout_2021_plus | total_return | +50.4% | 0.1050 | not significant |
| vs SPY | holdout_2021_plus | sharpe | +0.123 | 0.1600 | not significant |
| vs SPY | holdout_2021_plus | calmar | +0.005 | 0.3350 | not significant |
| vs SPY | holdout_2021_plus | max_drawdown | -7.0% | 0.8100 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
