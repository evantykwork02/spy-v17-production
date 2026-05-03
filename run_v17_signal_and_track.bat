@echo off
REM Weekly signal + duplicate-safe live paper tracking.
REM Run after Friday market close. If you accidentally rerun mid-week,
REM the tracker updates reports but does NOT create a fake next-Friday signal.

cd /d "%~dp0"
py spy_v17_conservative.py --mode signal --live-track
pause
