# SPY V17 Conservative - Treasury Live Test Runbook

## Weekly live run

Run every Friday after the US market close:

```bat
py spy_v17_conservative.py --mode signal --refresh-data --live-track
```

Then review:

- `outputs_v17_conservative/latest_signal.json`
- `outputs_v17_conservative/V17_REPORT.md`
- `live_tracker/LIVE_TRACKING_REPORT.md`
- `live_tracker/live_signal_ledger.csv`

## Preflight deployment audit

Run after the weekly signal if you want a fast operational health check:

```bat
py v17_deployment_audit.py --offline
```

Use the online version when you want it to refresh first:

```bat
py v17_deployment_audit.py --refresh-data
```

Main outputs:

- `deployment_audit/DEPLOYMENT_AUDIT_REPORT.md`
- `deployment_audit/deployment_audit_summary.csv`

## Monthly validation

```bat
py spy_v17_conservative.py --mode full --refresh-data --n-bootstrap 300 --n-random-rebalance 300 --n-synthetic 75 --n-bayes-draws 10000 --sensitivity-grid smoke
```

## Quarterly / deep validation

```bat
py spy_v17_conservative.py --mode full --refresh-data --n-bootstrap 2000 --n-random-rebalance 1000 --n-synthetic 100 --n-bayes-draws 20000 --sensitivity-grid smoke
```

Use `--sensitivity-grid full` only when you intentionally want the slowest parameter grid.

## Live test rules

1. Keep model logic frozen during the live test.
2. Record actual execution prices and commissions/slippage separately from the model tracker.
3. Compare actual live P&L against both SPY and the model tracker every week.
4. Do not use `--live-reset` unless intentionally restarting the paper/live test.
5. If the same signal week is rerun, the ledger should update the existing row instead of creating a duplicate.
6. Treat the backtest timing as a next-trading-day close-to-close proxy. Actual Monday-open fills can differ and must be tracked.
