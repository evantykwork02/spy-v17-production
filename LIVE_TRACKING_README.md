# V17 Live Tracking Feature

## What changed

This build adds a duplicate-safe live paper tracker to the original weekly V17 model.

The model is still the same weekly model:

```bat
Friday after market close -> run signal -> execute target weights on Monday
```

The tracker records what the model told you to hold, then tracks the live-paper performance versus SPY.

## Main command

```bat
py spy_v17_conservative.py --mode signal --live-track
```

Or double-click:

```text
run_v17_signal_and_track.bat
```

## Files created

The tracker writes files into:

```text
live_tracker/
```

Main files:

```text
LIVE_TRACKING_REPORT.md
live_signal_ledger.csv
live_equity_curve.csv
live_signal_periods.csv
live_summary.csv
live_summary.json
current_effective_weights.csv
```

## What each file means

### `live_signal_ledger.csv`

One row per Friday signal. This is the audit trail.

It stores:

- signal date
- estimated/actual Monday trade date
- V12 signal
- V17 signal
- regime
- exact target weights
- target allocation text

### `live_equity_curve.csv`

Daily paper performance of the model versus SPY from your first tracked signal.

It includes:

- model equity
- SPY benchmark equity
- model daily return
- SPY daily return
- drawdowns
- effective weights

### `live_signal_periods.csv`

Signal-by-signal attribution.

This helps you answer:

```text
Did this week's signal beat SPY?
Did defensive weeks help?
Did SPXL weeks help?
Did the model reduce drawdown?
```

### `LIVE_TRACKING_REPORT.md`

Human-readable dashboard summary.

## Duplicate-safe behaviour

The tracker is keyed by `signal_date`.

So if the latest real signal is:

```text
2026-04-24
```

and you accidentally run the program again before the next completed Friday close, the tracker will update reports but will not append another row.

You should see an action like:

```text
updated_existing_signal_no_duplicate
```

instead of:

```text
appended_new_signal
```

## Important bug fix added

The original pandas weekly resampling can do this:

```text
Run on Monday/Tuesday -> label the partial week as upcoming Friday
```

That is dangerous for a Friday-after-close system.

This build adds:

```python
resample_completed_friday_weeks()
```

That blocks fake future Friday signals. Accidental mid-week reruns keep the most recent completed Friday signal.

## Starting capital

Default paper capital is:

```text
10000
```

To change it:

```bat
py spy_v17_conservative.py --mode signal --live-track --live-start-cash 25000
```

## Reset tracker

Only use this if you intentionally want to restart live tracking:

```bat
py spy_v17_conservative.py --mode signal --live-track --live-reset
```

## Best live-testing rule

For a clean live test, do not edit model rules for 3-6 months.

Run the same command every Friday after market close:

```bat
py spy_v17_conservative.py --mode signal --live-track
```

Then execute the exact target allocation on Monday.
