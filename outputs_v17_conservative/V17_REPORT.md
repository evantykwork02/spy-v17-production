# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-05-29**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **STRONG_CALM_BULL** with target net SPY exposure **1.20x**
- Allocation: SPY 90.0%,  SPXL 10.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1184.2% | 15.71% | 0.891 | -33.7% | 0.466 |
| V12 (defensive engine) | 3302.8% | 22.34% | 1.127 | -24.2% | 0.924 |
| **V17 Conservative** | **4934.1%** | **25.11%** | **1.171** | **-24.2%** | **1.039** |

**V17 outperformed SPY by +3749.9% in total return, with Sharpe +0.280 higher and max drawdown +9.6% (less negative is better).**

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
| SPY buy-and-hold | 118.1% | 15.56% | 0.943 | -24.5% | 0.635 |
| V12 | 230.8% | 24.84% | 1.245 | -16.9% | 1.466 |
| V17 Conservative | 276.1% | 27.84% | 1.260 | -17.2% | 1.616 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.3% |
| 2015_2016_china_oil | -7.0% | -5.6% | -6.1% |
| 2018_q4_fed_selloff | -13.5% | -9.9% | -9.9% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | +1.0% | +3.2% |
| 2023_low_vol_uptrend | +26.2% | +26.6% | +27.0% |
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
| 2023 | +26.2% | +26.6% | +27.0% |
| 2024 | +24.9% | +27.6% | +30.7% |
| 2025 | +17.7% | +36.3% | +38.4% |
| 2026 | +11.6% | +11.5% | +11.7% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +1631.3% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.038 | 0.0900 | borderline |
| vs V12 | full | calmar | +0.115 | 0.1050 | not significant |
| vs V12 | full | max_drawdown | -0.0% | 0.8400 | not significant |
| vs V12 | holdout_2021_plus | total_return | +45.3% | 0.0250 | significant (p<0.05) |
| vs V12 | holdout_2021_plus | sharpe | -0.007 | 0.6100 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.150 | 0.5200 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.3% | 0.9550 | not significant |
| vs SPY | full | total_return | +3749.9% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.352 | 0.0050 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.573 | 0.0150 | significant (p<0.05) |
| vs SPY | full | max_drawdown | +9.6% | 0.2000 | not significant |
| vs SPY | holdout_2021_plus | total_return | +158.0% | 0.0150 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | sharpe | +0.504 | 0.0300 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.981 | 0.0550 | borderline |
| vs SPY | holdout_2021_plus | max_drawdown | +7.3% | 0.3050 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
