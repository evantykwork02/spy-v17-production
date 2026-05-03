@echo off
REM Offline test run for weekly signal + live tracker using cached data only.

cd /d "%~dp0"
py spy_v17_conservative.py --mode signal --offline --live-track
pause
