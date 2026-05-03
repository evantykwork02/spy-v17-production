@echo off
REM Quick weekly signal — fetches latest data and shows allocation.
REM Takes ~5 seconds if cache is recent, ~30-60s on first run.

cd /d "%~dp0"
py spy_v17_conservative.py --mode signal
pause
