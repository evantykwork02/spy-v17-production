# V17 Live Tracking — Local Test Report

## Result

The updated package was tested locally on the included offline cache.

## Tests completed

### 1. Weekly signal + live tracker

Command-equivalent tested:

```bat
py spy_v17_conservative.py --mode signal --offline --live-track --live-reset
```

Result:

- Completed successfully.
- Latest completed signal date: 2026-04-24.
- Ledger created with one row.
- Live tracker files created.

### 2. Duplicate-safe rerun

Command-equivalent tested:

```bat
py spy_v17_conservative.py --mode signal --offline --live-track
```

Result:

- Completed successfully.
- Tracker action: `updated_existing_signal_no_duplicate`.
- Ledger stayed at one row.
- No fake future signal was appended.

### 3. Partial-week / fake-next-Friday safety

A fake Monday row after the latest completed Friday was injected into the daily data.

Result:

- Latest weekly signal remained 2026-04-24.
- It did **not** jump to the upcoming Friday label.
- This confirms the completed-Friday resampling safety guard works.

### 4. Multi-week live-tracker simulation

Historical sequential signal updates were simulated for:

- 2026-03-13
- 2026-03-20
- 2026-03-27
- 2026-04-03

Result:

- New weeks appended correctly.
- Rerunning the same week updated the existing row instead of duplicating it.
- Equity curve and period attribution files were created.

### 5. Heavy validation pipeline smoke test

Command-equivalent tested:

```bat
py spy_v17_conservative.py --mode full --offline --n-bootstrap 80 --n-random-rebalance 80 --n-synthetic 20 --n-bayes-draws 2500 --sensitivity-grid smoke
```

Result:

- Completed successfully.
- All heavy validation components ran:
  - block bootstrap
  - random rebalance comparison
  - synthetic null markets
  - stratified regime test
  - deflated Sharpe ratio
  - Bayesian Sharpe credible interval
  - yearly consistency
  - rolling windows
  - cost stress test
  - parameter sensitivity smoke grid

Generated heavy files included:

- `HEAVY_VALIDATION_REPORT.md`
- `heavy_bootstrap.csv`
- `heavy_random_rebalance.csv`
- `heavy_synthetic_null.csv`
- `heavy_stratified_regime.csv`
- `heavy_deflated_sharpe.csv`
- `heavy_bayesian_sharpe.csv`
- `heavy_yearly_consistency.csv`
- `heavy_rolling_summary.csv`
- `heavy_cost_stress.csv`
- `heavy_parameter_sensitivity.csv`

## Extra robustness fix added

The data cache now supports both:

- `data/daily_cache.parquet`
- `data/daily_cache.csv`

If a local pandas/pyarrow installation has a Parquet engine issue, the program can fall back to CSV.

The requirements file also pins pandas/pyarrow more safely:

```text
pandas>=2.0,<2.3
pyarrow>=12,<20
```

This avoids a pyarrow compatibility issue seen in this runtime.
