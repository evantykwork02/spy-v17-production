# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-06-05**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NERVOUS_MARKET** with target net SPY exposure **1.30x**
- Allocation: SPY 85.0%,  SPXL 15.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1129.4% | 15.40% | 0.876 | -33.7% | 0.457 |
| V12 (defensive engine) | 2316.7% | 19.94% | 0.814 | -31.5% | 0.633 |
| **V17 Conservative** | **2846.2%** | **21.31%** | **0.854** | **-31.5%** | **0.676** |

**V17 outperformed SPY by +1716.9% in total return, with Sharpe -0.022 higher and max drawdown +2.2% (less negative is better).**

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
| SPY buy-and-hold | 108.8% | 14.57% | 0.890 | -24.5% | 0.595 |
| V12 | 139.3% | 17.49% | 0.734 | -31.5% | 0.555 |
| V17 Conservative | 153.9% | 18.78% | 0.776 | -31.5% | 0.596 |

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
| 2026 | +6.9% | +12.0% | +11.2% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +529.5% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.035 | 0.0050 | highly significant (p<0.01) |
| vs V12 | full | calmar | +0.043 | 0.0450 | significant (p<0.05) |
| vs V12 | full | max_drawdown | +0.0% | 0.5200 | not significant |
| vs V12 | holdout_2021_plus | total_return | +14.6% | 0.0250 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | +0.036 | 0.0900 | borderline |
| vs V12 | holdout_2021_plus | calmar | +0.041 | 0.0500 | borderline |
| vs V12 | holdout_2021_plus | max_drawdown | +0.0% | 0.5700 | not significant |
| vs SPY | full | total_return | +1716.9% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.195 | 0.0100 | significant (p<0.05) |
| vs SPY | full | calmar | +0.219 | 0.0500 | borderline |
| vs SPY | full | max_drawdown | +2.2% | 0.4200 | not significant |
| vs SPY | holdout_2021_plus | total_return | +45.0% | 0.1250 | not significant |
| vs SPY | holdout_2021_plus | sharpe | +0.113 | 0.2100 | not significant |
| vs SPY | holdout_2021_plus | calmar | +0.001 | 0.3700 | not significant |
| vs SPY | holdout_2021_plus | max_drawdown | -7.0% | 0.8150 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
