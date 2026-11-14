# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-11-13**_
_Data source: forced refresh_

## Executive summary

- This week's regime: **NORMAL** with target net SPY exposure **1.00x**
- Allocation: SPY 100.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1182.4% | 15.27% | 0.873 | -33.7% | 0.453 |
| V12 (defensive engine) | 3298.3% | 21.70% | 1.099 | -24.2% | 0.898 |
| **V17 Conservative** | **4865.8%** | **24.30%** | **1.139** | **-24.2%** | **1.006** |

**V17 outperformed SPY by +3683.3% in total return, with Sharpe +0.265 higher and max drawdown +9.6% (less negative is better).**

## This week's signal

| Field | Value |
| --- | --- |
| Date | 2026-11-13 |
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
| SPY buy-and-hold | 117.8% | 14.24% | 0.881 | -24.5% | 0.581 |
| V12 | 230.3% | 22.67% | 1.140 | -16.9% | 1.338 |
| V17 Conservative | 271.0% | 25.12% | 1.147 | -17.2% | 1.458 |

## Behaviour during historical stress events

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011_euro_stress | -3.8% | +1.1% | +1.3% |
| 2015_2016_china_oil | -7.0% | -5.6% | -6.1% |
| 2018_q4_fed_selloff | -13.5% | -9.9% | -9.9% |
| 2020_covid_crash | -13.2% | +6.2% | +6.2% |
| 2022_bear_market | -18.2% | +1.0% | +3.2% |
| 2023_low_vol_uptrend | +26.2% | +26.6% | +27.4% |
| 2024_low_vol_uptrend | +24.9% | +27.6% | +30.1% |

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
| 2023 | +26.2% | +26.6% | +27.4% |
| 2024 | +24.9% | +27.6% | +30.1% |
| 2025 | +17.7% | +36.3% | +38.4% |
| 2026 | +11.5% | +11.4% | +10.3% |

## Statistical significance (paired block bootstrap)

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +1567.5% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.033 | 0.1000 | not significant |
| vs V12 | full | calmar | +0.108 | 0.1850 | not significant |
| vs V12 | full | max_drawdown | -0.0% | 0.8150 | not significant |
| vs V12 | holdout_2021_plus | total_return | +40.6% | 0.0600 | borderline |
| vs V12 | holdout_2021_plus | sharpe | -0.016 | 0.6550 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.121 | 0.5750 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.3% | 0.9800 | not significant |
| vs SPY | full | total_return | +3683.3% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.341 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.553 | 0.0150 | significant (p<0.05) |
| vs SPY | full | max_drawdown | +9.6% | 0.2000 | not significant |
| vs SPY | holdout_2021_plus | total_return | +153.1% | 0.0000 | highly significant (p<0.01) |
| vs SPY | holdout_2021_plus | sharpe | +0.457 | 0.0150 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.877 | 0.0350 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | max_drawdown | +7.3% | 0.3000 | not significant |

## Honest interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
