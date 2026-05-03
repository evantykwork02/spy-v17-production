@echo off
REM Faster heavy-validation diagnostic run.

cd /d "%~dp0"
py spy_v17_conservative.py --mode full --n-bootstrap 300 --n-random-rebalance 300 --n-synthetic 75 --n-bayes-draws 10000
pause
