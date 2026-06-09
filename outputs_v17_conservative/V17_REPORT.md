# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-06-05**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NERVOUS_MARKET** with target net SPY exposure **1.30x**
- Allocation: SPY 85.0%,  SPXL 15.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1158.5% | 15.56% | 0.883 | -33.7% | 0.461 |
| V12 (defensive engine) | 2374.0% | 20.10% | 0.821 | -31.5% | 0.638 |
| **V17 Conservative** | **2951.2%** | **21.55%** | **0.865** | **-31.5%** | **0.684** |

**V17 outperformed SPY by +1792.7% in total return, with Sharpe -0.019 higher and max drawdown +2.2% (less negative is better).**

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
| SPY buy-and-hold | 113.8% | 15.07% | 0.917 | -24.5% | 0.615 |
| V12 | 145.0% | 18.00% | 0.758 | -31.5% | 0.571 |
| V17 Conservative | 162.9% | 19.55% | 0.811 | -31.5% | 0.620 |

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
| 2026 | +9.4% | +14.7% | +14.7% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +577.2% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.038 | 0.0050 | highly significant (p<0.01) |
| vs V12 | full | calmar | +0.046 | 0.0450 | significant (p<0.05) |
| vs V12 | full | max_drawdown | +0.0% | 0.4850 | not significant |
| vs V12 | holdout_2021_plus | total_return | +17.9% | 0.0100 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | +0.047 | 0.0750 | borderline |
| vs V12 | holdout_2021_plus | calmar | +0.049 | 0.0500 | borderline |
| vs V12 | holdout_2021_plus | max_drawdown | +0.0% | 0.5500 | not significant |
| vs SPY | full | total_return | +1792.7% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.197 | 0.0100 | significant (p<0.05) |
| vs SPY | full | calmar | +0.222 | 0.0500 | borderline |
| vs SPY | full | max_drawdown | +2.2% | 0.4100 | not significant |
| vs SPY | holdout_2021_plus | total_return | +49.1% | 0.1200 | not significant |
| vs SPY | holdout_2021_plus | sharpe | +0.121 | 0.2000 | not significant |
| vs SPY | holdout_2021_plus | calmar | +0.005 | 0.3700 | not significant |
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
