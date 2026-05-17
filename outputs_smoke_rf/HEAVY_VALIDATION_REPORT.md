# V17 Conservative — Heavy Validation Report

This report is designed to test whether V17's edge is genuine rather than just a lucky backtest. It is intentionally stricter than the normal performance report.

## Method note

- Block bootstrap resamples chunks of time to preserve serial dependence and mini-regimes.
- Random rebalance keeps V17's exact exposure distribution but destroys timing.
- Synthetic null markets preserve approximate SPY variance/autocorrelation but remove historical regime structure.
- Deflated Sharpe adjusts the Sharpe estimate for non-normal returns and the fact that many variants were tested.

Assumed model-development trials for Deflated Sharpe: **80**.

## 1. Block bootstrap

| new_model        | base_model | period            | metric       | observed_delta | p_fail | bootstrap_mean_delta | n_bootstrap | block_len |
| ---------------- | ---------- | ----------------- | ------------ | -------------- | ------ | -------------------- | ----------- | --------- |
| v17_conservative | v12        | full              | total_return | 8.0487         | 0.0000 | 17.4640              | 10          | 21        |
| v17_conservative | v12        | full              | sharpe       | 0.0237         | 0.2000 | 0.0150               | 10          | 21        |
| v17_conservative | v12        | full              | calmar       | 0.0601         | 0.2000 | 0.0307               | 10          | 21        |
| v17_conservative | v12        | full              | max_drawdown | -0.0008        | 0.8000 | -0.0052              | 10          | 21        |
| v17_conservative | v12        | holdout_2021_plus | total_return | 0.2318         | 0.0000 | 0.2105               | 10          | 21        |
| v17_conservative | v12        | holdout_2021_plus | sharpe       | 0.0093         | 0.3000 | 0.0139               | 10          | 21        |
| v17_conservative | v12        | holdout_2021_plus | calmar       | 0.0687         | 0.4000 | 0.0274               | 10          | 21        |
| v17_conservative | v12        | holdout_2021_plus | max_drawdown | -0.0031        | 1.0000 | -0.0100              | 10          | 21        |
| v17_conservative | SPY_BH     | full              | total_return | 28.6762        | 0.0000 | 38.2749              | 10          | 21        |
| v17_conservative | SPY_BH     | full              | sharpe       | 0.3374         | 0.0000 | 0.3136               | 10          | 21        |
| v17_conservative | SPY_BH     | full              | calmar       | 0.5173         | 0.0000 | 0.3227               | 10          | 21        |
| v17_conservative | SPY_BH     | full              | max_drawdown | 0.0947         | 0.2000 | 0.0559               | 10          | 21        |
| v17_conservative | SPY_BH     | holdout_2021_plus | total_return | 1.3287         | 0.1000 | 1.3287               | 10          | 21        |
| v17_conservative | SPY_BH     | holdout_2021_plus | sharpe       | 0.5137         | 0.1000 | 0.5462               | 10          | 21        |
| v17_conservative | SPY_BH     | holdout_2021_plus | calmar       | 0.8937         | 0.1000 | 0.5866               | 10          | 21        |
| v17_conservative | SPY_BH     | holdout_2021_plus | max_drawdown | 0.0724         | 0.3000 | 0.0396               | 10          | 21        |

## 2. Random rebalance timing test

| metric       | actual  | random_mean | random_p95 | p_random_beats_actual | n_random |
| ------------ | ------- | ----------- | ---------- | --------------------- | -------- |
| total_return | 40.1790 | 8.9875      | 12.9964    | 0.0000                | 10       |
| sharpe       | 1.1446  | 0.6632      | 0.7723     | 0.0000                | 10       |
| calmar       | 0.9792  | 0.3716      | 0.4697     | 0.0000                | 10       |
| max_drawdown | -0.2425 | -0.3769     | -0.3417    | 0.0000                | 10       |

## 3. Synthetic null market test

| metric       | observed_delta_v17_minus_spy | null_mean_delta | null_p95_delta | p_synthetic_beats_observed | n_synthetic |
| ------------ | ---------------------------- | --------------- | -------------- | -------------------------- | ----------- |
| total_return | 28.6762                      | -2.4160         | 0.2669         | 0.0000                     | 2           |
| sharpe       | 0.3374                       | -0.1305         | -0.0865        | 0.0000                     | 2           |
| calmar       | 0.5173                       | -0.1238         | -0.1044        | 0.0000                     | 2           |
| max_drawdown | 0.0947                       | -0.0627         | -0.0333        | 0.0000                     | 2           |

## 4. Stratified regime test

| regime          | days | v17_total_return | v12_total_return | spy_total_return | v17_sharpe | v12_sharpe | spy_sharpe | annualized_mean_return_delta_v17_minus_v12 | p_fail_mean_return_vs_v12 |
| --------------- | ---- | ---------------- | ---------------- | ---------------- | ---------- | ---------- | ---------- | ------------------------------------------ | ------------------------- |
| DUAL_BOOST      | 708  | 1.0349           | 0.8172           | 0.8164           | 1.9025     | 1.9568     | 1.9571     | 0.0435                                     | 0.0000                    |
| YC_BOOST        | 722  | 1.0053           | 0.8941           | 0.8732           | 1.3577     | 1.3738     | 1.3547     | 0.0232                                     | 0.0020                    |
| CALM_BULL_BOOST | 956  | 0.6365           | 0.6039           | 0.5813           | 1.1137     | 1.1290     | 1.0984     | 0.0060                                     | 0.0740                    |
| NERVOUS_MARKET  | 274  | 0.3138           | 0.2630           | 0.3216           | 1.1909     | 1.1388     | 1.3513     | 0.0417                                     | 0.0460                    |
| NORMAL          | 728  | -0.0707          | -0.0695          | -0.0638          | -0.2194    | -0.2184    | -0.2036    | -0.0003                                    | 0.4940                    |
| LEVERAGED_LONG  | 544  | 3.8485           | 3.8847           | 1.6834           | 2.3717     | 2.3843     | 2.1873     | -0.0034                                    | 0.8860                    |
| DEFENSIVE       | 378  | 0.0055           | 0.0077           | -0.1285          | 0.0792     | 0.0849     | -0.0803    | -0.0012                                    | 0.5040                    |
| CRASH_SHORT     | 88   | 0.0361           | 0.0374           | -0.1969          | 0.4219     | 0.4358     | -2.2562    | -0.0036                                    | 1.0000                    |

## 5. Deflated Sharpe Ratio

| model            | n    | assumed_trials | annual_sharpe | daily_sharpe | deflated_threshold_daily | deflated_threshold_annual | deflated_sharpe_probability | skew    | kurtosis |
| ---------------- | ---- | -------------- | ------------- | ------------ | ------------------------ | ------------------------- | --------------------------- | ------- | -------- |
| SPY_BH           | 4398 | 80             | 0.8072        | 0.0509       | 0.0374                   | 0.5936                    | 0.8111                      | -0.2976 | 13.9555  |
| v12              | 4398 | 80             | 1.1210        | 0.0706       | 0.0370                   | 0.5871                    | 0.9871                      | 0.1846  | 12.2881  |
| v17_conservative | 4398 | 80             | 1.1446        | 0.0721       | 0.0370                   | 0.5879                    | 0.9899                      | 0.1223  | 10.7961  |

## 6. Bayesian Sharpe credible interval

| model            | draws | sharpe_mean | sharpe_p05 | sharpe_p50 | sharpe_p95 | prob_sharpe_gt_0 | prob_sharpe_gt_spy | prob_sharpe_gt_v12 |
| ---------------- | ----- | ----------- | ---------- | ---------- | ---------- | ---------------- | ------------------ | ------------------ |
| SPY_BH           | 100   | 0.8304      | 0.4632     | 0.8067     | 1.2298     | 1.0000           |                    |                    |
| v12              | 100   | 1.1867      | 0.8468     | 1.1486     | 1.5883     | 1.0000           |                    |                    |
| v17_conservative | 100   | 1.1302      | 0.8096     | 1.1018     | 1.4759     | 1.0000           | 0.8300             | 0.4400             |

## 7. Yearly walk-forward consistency

| metric       | base_model | years | wins | win_rate | binomial_p_value |
| ------------ | ---------- | ----- | ---- | -------- | ---------------- |
| total_return | SPY_BH     | 18    | 15   | 0.8333   | 0.0038           |
| total_return | v12        | 18    | 14   | 0.7778   | 0.0154           |
| sharpe       | SPY_BH     | 18    | 14   | 0.7778   | 0.0154           |
| sharpe       | v12        | 18    | 11   | 0.6111   | 0.2403           |
| calmar       | SPY_BH     | 18    | 15   | 0.8333   | 0.0038           |
| calmar       | v12        | 18    | 11   | 0.6111   | 0.2403           |
| max_drawdown | SPY_BH     | 18    | 8    | 0.4444   | 0.7597           |
| max_drawdown | v12        | 18    | 0    | 0.0000   | 1.0000           |

## 8. Rolling 1y/3y/5y windows

| horizon_years | n_windows | pct_v17_beats_spy_return | pct_v17_beats_v12_return | pct_v17_beats_spy_sharpe | pct_v17_beats_v12_sharpe | median_return_delta_v17_minus_spy | median_return_delta_v17_minus_v12 |
| ------------- | --------- | ------------------------ | ------------------------ | ------------------------ | ------------------------ | --------------------------------- | --------------------------------- |
| 1.0000        | 198.0000  | 0.9040                   | 0.8232                   | 0.7424                   | 0.5707                   | 0.0438                            | 0.0112                            |
| 3.0000        | 174.0000  | 0.9885                   | 1.0000                   | 0.8448                   | 0.7356                   | 0.1898                            | 0.0456                            |
| 5.0000        | 150.0000  | 1.0000                   | 1.0000                   | 0.8533                   | 0.8533                   | 0.5090                            | 0.1490                            |

## 9. Cost stress

| period            | model            | n    | total_return | cagr   | annual_vol | sharpe | max_drawdown | calmar | hit_rate | avg_exposure | pct_levered | pct_short | tc_bps  |
| ----------------- | ---------------- | ---- | ------------ | ------ | ---------- | ------ | ------------ | ------ | -------- | ------------ | ----------- | --------- | ------- |
| holdout_2021_plus | SPY_BH           | 1348 | 1.1237       | 0.1512 | 0.1691     | 0.7174 | -0.2450      | 0.6172 | 0.5460   | 1.0000       | 0.0000      | 0.0000    | 0.0000  |
| holdout_2021_plus | v12              | 1348 | 2.2678       | 0.2478 | 0.1621     | 1.2385 | -0.1673      | 1.4812 | 0.5542   | 0.9002       | 0.0964      | 0.0512    | 0.0000  |
| holdout_2021_plus | v17_conservative | 1348 | 2.5083       | 0.2645 | 0.1729     | 1.2483 | -0.1702      | 1.5538 | 0.5549   | 0.9833       | 0.7574      | 0.0512    | 0.0000  |
| holdout_2021_plus | SPY_BH           | 1348 | 1.1237       | 0.1512 | 0.1691     | 0.7174 | -0.2450      | 0.6172 | 0.5460   | 1.0000       | 0.0000      | 0.0000    | 5.0000  |
| holdout_2021_plus | v12              | 1348 | 2.2206       | 0.2444 | 0.1621     | 1.2219 | -0.1695      | 1.4422 | 0.5534   | 0.9002       | 0.0964      | 0.0512    | 5.0000  |
| holdout_2021_plus | v17_conservative | 1348 | 2.4524       | 0.2607 | 0.1729     | 1.2312 | -0.1725      | 1.5109 | 0.5542   | 0.9833       | 0.7574      | 0.0512    | 5.0000  |
| holdout_2021_plus | SPY_BH           | 1348 | 1.1237       | 0.1512 | 0.1691     | 0.7174 | -0.2450      | 0.6172 | 0.5460   | 1.0000       | 0.0000      | 0.0000    | 10.0000 |
| holdout_2021_plus | v12              | 1348 | 2.1740       | 0.2410 | 0.1620     | 1.2052 | -0.1716      | 1.4042 | 0.5527   | 0.9002       | 0.0964      | 0.0512    | 10.0000 |
| holdout_2021_plus | v17_conservative | 1348 | 2.3974       | 0.2569 | 0.1728     | 1.2139 | -0.1748      | 1.4692 | 0.5534   | 0.9833       | 0.7574      | 0.0512    | 10.0000 |
| holdout_2021_plus | SPY_BH           | 1348 | 1.1237       | 0.1512 | 0.1691     | 0.7174 | -0.2450      | 0.6172 | 0.5460   | 1.0000       | 0.0000      | 0.0000    | 20.0000 |
| holdout_2021_plus | v12              | 1348 | 2.0829       | 0.2343 | 0.1620     | 1.1717 | -0.1763      | 1.3285 | 0.5497   | 0.9002       | 0.0964      | 0.0512    | 20.0000 |
| holdout_2021_plus | v17_conservative | 1348 | 2.2899       | 0.2494 | 0.1728     | 1.1793 | -0.1797      | 1.3878 | 0.5519   | 0.9833       | 0.7574      | 0.0512    | 20.0000 |
| holdout_2021_plus | SPY_BH           | 1348 | 1.1237       | 0.1512 | 0.1691     | 0.7174 | -0.2450      | 0.6172 | 0.5460   | 1.0000       | 0.0000      | 0.0000    | 30.0000 |
| holdout_2021_plus | v12              | 1348 | 1.9942       | 0.2275 | 0.1620     | 1.1380 | -0.1812      | 1.2556 | 0.5482   | 0.9002       | 0.0964      | 0.0512    | 30.0000 |
| holdout_2021_plus | v17_conservative | 1348 | 2.1857       | 0.2419 | 0.1728     | 1.1445 | -0.1848      | 1.3089 | 0.5497   | 0.9833       | 0.7574      | 0.0512    | 30.0000 |

## 10. Parameter sensitivity summary

No rows generated.

## Overall automated verdict

- PASS: V17 Sharpe is in the upper tail versus random schedules with the same exposure distribution.
- PASS: V17 return edge is stronger than most synthetic no-regime markets.
- PASS: Deflated Sharpe probability is above 95% after multiple-testing adjustment.
