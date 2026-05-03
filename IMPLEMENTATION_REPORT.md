# V17 Live Tracking Implementation Report

## Implemented

Added a duplicate-safe live paper tracker to the original weekly V17 model.

New command:

```bat
py spy_v17_conservative.py --mode signal --live-track
```

New files:

```text
v17_live_tracker.py
LIVE_TRACKING_README.md
run_v17_signal_and_track.bat
run_v17_signal_and_track_offline.bat
```

## Critical live-run bug fixed

The original code used:

```python
daily.resample("W-FRI").last()
```

That is risky for live use because if you rerun on Monday/Tuesday, pandas can label the partial current week as the upcoming Friday.

Example:

```text
Actual data through Monday 2026-04-27
Plain pandas W-FRI label: 2026-05-01
Correct latest completed signal: 2026-04-24
```

Fix added:

```python
resample_completed_friday_weeks()
```

The program now only uses completed Friday-labelled weeks. A mid-week accidental rerun will keep the previous completed Friday signal instead of creating a fake future signal.

## Live tracker behaviour

The tracker is keyed by `signal_date`.

If the signal date already exists in:

```text
live_tracker/live_signal_ledger.csv
```

the tracker updates that row and reports:

```text
updated_existing_signal_no_duplicate
```

It does not append a duplicate row.

## Files written by tracker

```text
live_tracker/LIVE_TRACKING_REPORT.md
live_tracker/live_signal_ledger.csv
live_tracker/live_equity_curve.csv
live_tracker/live_signal_periods.csv
live_tracker/live_summary.csv
live_tracker/live_summary.json
live_tracker/current_effective_weights.csv
```

## Validation done here

I tested:

1. Script compiles successfully.
2. Live tracker first run appends one signal row.
3. Running the same signal again does not create a duplicate row.
4. The ledger remained at 1 row after rerun.
5. The tracker action correctly changed to:

```text
updated_existing_signal_no_duplicate
```

6. The partial-week resampling bug was checked using a mock Monday rerun:
   - plain pandas produced fake label `2026-05-01`
   - fixed helper correctly kept `2026-04-24`

## Important assumption

The tracker uses the same execution convention as the backtest:

```text
Friday signal becomes effective on the next available trading day's close-to-close return.
```

This is consistent with the current V17 backtest methodology. If you want exact broker-level tracking later, you can add manual Monday fill prices, but this version is cleaner for model-vs-SPY paper tracking.
