@echo off
REM Full heavy validation run.
REM This can take 10-15 minutes depending on your machine.

cd /d "%~dp0"
py spy_v17_conservative.py --mode full --n-bootstrap 2000 --n-random-rebalance 1000 --n-synthetic 100 --n-bayes-draws 20000
pause
