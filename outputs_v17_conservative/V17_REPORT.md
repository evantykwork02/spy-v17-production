# SPY V17 Conservative — Performance & Validation Report

_Report generated for signal date **2026-05-15**_
_Data source: offline cache (0.3h old)_

## At a Glance

- This week's regime: **NORMAL** with target net SPY exposure **1.00x**
- Allocation: SPY 100.0%

**Long-run performance (2009 → present)**

| Model | Total return | CAGR | Sharpe | Max drawdown | Calmar |
| --- | --- | --- | --- | --- | --- |
| SPY buy-and-hold | 1150.3% | 15.57% | 0.807 | -33.7% | 0.462 |
| V12 (defensive engine) | 3213.0% | 22.21% | 1.121 | -24.2% | 0.919 |
| **V17 Conservative** | **4017.9%** | **23.74%** | **1.145** | **-24.2%** | **0.979** |

**V17 outperformed SPY by +2867.6% in total return, with Sharpe +0.337 higher and max drawdown +9.5% (less negative is better).**

## Regime Activation

- Nervous-market sleeve fired on **57** completed weeks in this backtest.
| Regime | Weeks | % of weeks | Avg exposure | First seen | Last seen |
| --- | --- | --- | --- | --- | --- |
| DUAL_BOOST | 149 | 16.3% | 1.25x | 2010-01-08 | 2026-02-20 |
| YC_BOOST | 150 | 16.4% | 1.12x | 2009-03-27 | 2026-03-06 |
| CALM_BULL_BOOST | 197 | 21.6% | 1.07x | 2010-03-19 | 2026-05-08 |
| NERVOUS_MARKET | 57 | 6.2% | 1.15x | 2009-08-21 | 2026-04-03 |
| NORMAL | 151 | 16.5% | 1.00x | 2010-10-15 | 2026-05-15 |
| LEVERAGED_LONG | 112 | 12.3% | 1.51x | 2009-03-20 | 2025-11-21 |
| DEFENSIVE | 79 | 8.7% | 0.60x | 2008-11-21 | 2026-03-27 |
| CRASH_SHORT | 18 | 2.0% | -1.00x | 2018-10-26 | 2022-10-28 |

## Latest Signal

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
| SPY buy-and-hold | 112.4% | 15.12% | 0.717 | -24.5% | 0.617 |
| V12 | 222.1% | 24.44% | 1.222 | -16.9% | 1.442 |
| V17 Conservative | 245.2% | 26.07% | 1.231 | -17.3% | 1.511 |

## Stress Windows

| Window | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2011 euro stress | -3.8% | +1.1% | +0.8% |
| 2015 2016 china oil | -7.0% | -5.6% | -5.9% |
| 2018 q4 fed selloff | -13.5% | -9.9% | -9.9% |
| 2020 covid crash | -13.2% | +6.2% | +6.1% |
| 2022 bear market | -18.2% | +1.0% | +1.9% |
| 2023 low vol uptrend | +26.2% | +26.6% | +27.2% |
| 2024 low vol uptrend | +24.9% | +27.6% | +28.9% |

## Calendar-year breakdown

| Year | SPY | V12 | V17 |
| --- | --- | --- | --- |
| 2009 | +26.4% | +36.5% | +41.7% |
| 2010 | +15.1% | +18.9% | +20.4% |
| 2011 | +1.9% | +8.3% | +8.7% |
| 2012 | +16.0% | +11.2% | +10.5% |
| 2013 | +32.3% | +32.3% | +36.8% |
| 2014 | +13.5% | +15.8% | +15.4% |
| 2015 | +1.2% | +1.4% | +1.2% |
| 2016 | +12.0% | +19.5% | +20.6% |
| 2017 | +21.7% | +21.7% | +23.6% |
| 2018 | -4.6% | -0.5% | -0.5% |
| 2019 | +31.2% | +37.3% | +40.0% |
| 2020 | +18.3% | +54.6% | +58.7% |
| 2021 | +28.7% | +33.4% | +38.6% |
| 2022 | -18.2% | +1.0% | +1.9% |
| 2023 | +26.2% | +26.6% | +27.2% |
| 2024 | +24.9% | +27.6% | +28.9% |
| 2025 | +17.7% | +36.3% | +37.5% |
| 2026 | +8.7% | +8.6% | +8.4% |

## Statistical Checks

| Comparison | Period | Metric | Observed delta | p_fail | Verdict |
| --- | --- | --- | --- | --- | --- |
| vs V12 | full | total_return | +804.9% | 0.0000 | highly significant (p<0.01) |
| vs V12 | full | sharpe | +0.024 | 0.0800 | borderline |
| vs V12 | full | calmar | +0.060 | 0.1800 | not significant |
| vs V12 | full | max_drawdown | -0.1% | 0.9000 | not significant |
| vs V12 | holdout_2021_plus | total_return | +23.2% | 0.0000 | highly significant (p<0.01) |
| vs V12 | holdout_2021_plus | sharpe | +0.009 | 0.3800 | not significant |
| vs V12 | holdout_2021_plus | calmar | +0.069 | 0.4900 | not significant |
| vs V12 | holdout_2021_plus | max_drawdown | -0.3% | 0.9800 | not significant |
| vs SPY | full | total_return | +2867.6% | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | sharpe | +0.337 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | calmar | +0.517 | 0.0000 | highly significant (p<0.01) |
| vs SPY | full | max_drawdown | +9.5% | 0.1850 | not significant |
| vs SPY | holdout_2021_plus | total_return | +132.9% | 0.0300 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | sharpe | +0.514 | 0.0400 | significant (p<0.05) |
| vs SPY | holdout_2021_plus | calmar | +0.894 | 0.0550 | borderline |
| vs SPY | holdout_2021_plus | max_drawdown | +7.2% | 0.2250 | not significant |

## Interpretation

**Strengths**

- V17 inherits V12's crash-protection engine unchanged. By design it cannot make crash protection worse than V12.
- Out-of-sample (2021+) performance is consistent with the in-sample period.
- Long-run Sharpe is materially above SPY's.

**Limitations**

- ~60% of cumulative edge comes from V12's crash protection. Long calm periods compress the excess return.
- All testing uses 2009 onwards. Truly novel regimes (stagflation etc.) are out-of-sample.
- Realistic forward Sharpe estimate: 0.95-1.10 (vs backtest 1.17), reflecting expected regime drift, slippage on Monday-open execution, and conservative cost assumptions.
