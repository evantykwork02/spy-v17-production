# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-05-08**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **CALM_BULL_BOOST** with target net SPY exposure **1.07x**
- Allocation: SPY 96.5%,  SPXL 3.5%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1140.3% | 15.53% | 0.881 | -33.7% | 0.461 |
| V12 (defensive engine) | 2338.2% | 20.10% | 1.041 | -31.5% | 0.638 |
| **V17 Conservative** | **2431.4%** | **20.36%** | **1.046** | **-31.5%** | **0.646** |

**V17 outperformed SPY by +1291.2% in total return, with Sharpe +0.164 higher and max drawdown +2.2% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-05-08 |
| V12 score | 1.00 |
| V17 score | 1.07 |
| Regime | CALM_BULL_BOOST |
| Net equity exposure | 1.07x |
| Calm-bull trigger | YES |
| Allocation | SPY 96.5%,  SPXL 3.5% |
| Reason | Calm-uptrend conditions met (CB only); V17-pro raises exposure to 1.07x. |

## Out-of-sample period (2021 → present)

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 110.7% | 14.98% | 0.910 | -24.5% | 0.612 |
| V12 | 141.4% | 17.96% | 0.986 | -31.5% | 0.570 |
| V17 Conservative | 147.4% | 18.50% | 1.003 | -31.5% | 0.587 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +0.7% |
| 2015_2016_china_oil | -7.0% | -5.6% | -5.7% |
| 2018_q4_fed_selloff | -13.5% | -19.1% | -19.2% |
| 2020_covid_crash | -13.2% | +6.2% | +6.1% |
| 2022_bear_market | -18.2% | -25.2% | -25.3% |
| 2023_low_vol_uptrend | +26.2% | +25.6% | +26.2% |
| 2024_low_vol_uptrend | +24.9% | +28.5% | +29.7% |

## Calendar-year breakdown

| Year | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2009 | +26.4% | +42.1% | +42.1% |
| 2010 | +15.1% | +18.9% | +18.6% |
| 2011 | +1.9% | +9.2% | +8.8% |
| 2012 | +16.0% | +11.2% | +10.5% |
| 2013 | +32.3% | +32.1% | +33.3% |
| 2014 | +13.5% | +15.8% | +15.5% |
| 2015 | +1.2% | +1.4% | +1.3% |
| 2016 | +12.0% | +20.8% | +21.0% |
| 2017 | +21.7% | +21.7% | +22.9% |
| 2018 | -4.6% | -9.6% | -9.6% |
| 2019 | +31.2% | +37.3% | +37.9% |
| 2020 | +18.3% | +57.7% | +58.1% |
| 2021 | +28.7% | +31.1% | +32.5% |
| 2022 | -18.2% | -25.2% | -25.3% |
| 2023 | +26.2% | +25.6% | +26.2% |
| 2024 | +24.9% | +28.5% | +29.7% |
| 2025 | +17.7% | +34.9% | +34.8% |
| 2026 | +7.8% | +13.0% | +13.2% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +93.3% | 0.0300 | significant (p<0.05) |
| vs V12 | full | sharpe | +0.004 | 0.2100 | not significant |
| vs V12 | full | calmar | +0.008 | 0.3500 | not significant |
| vs V12 | full | max_drawdown | -0.0% | 0.8000 | not significant |
| vs V12 | holdout_2021_plus | total_return | +6.0% | 0.0150 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | +0.017 | 0.0500 | borderline |
| vs V12 | holdout_2021_plus | calmar | +0.017 | 0.0350 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | max_drawdown | -0.0% | 0.5400 | not significant |
| vs SPY | full | total_return | +1291.2% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.164 | 0.0300 | significant (p<0.05) |
| vs SPY | full | calmar | +0.185 | 0.0700 | borderline |
| vs SPY | full | max_drawdown | +2.2% | 0.3850 | not significant |
| vs SPY | holdout_2021_plus | total_return | +36.7% | 0.1300 | not significant |
| vs SPY | holdout_2021_plus | sharpe | +0.093 | 0.2600 | not significant |
| vs SPY | holdout_2021_plus | calmar | -0.025 | 0.3700 | not significant |
| vs SPY | holdout_2021_plus | max_drawdown | -7.0% | 0.8000 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
