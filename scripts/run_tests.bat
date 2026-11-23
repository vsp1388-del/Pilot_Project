@echo off
rem Run all validation suites on Windows using the project .venv.
rem Extra args go to robot, e.g. scripts\run_tests.bat --include counts
setlocal
cd /d "%~dp0.."
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
if "%RESULTS_DIR%"=="" set "RESULTS_DIR=results"

"%PY%" scripts\wait_for_db.py || exit /b 2
"%PY%" -m robot --pythonpath . --outputdir "%RESULTS_DIR%" %* tests
set RC=%ERRORLEVEL%
"%PY%" scripts\summarize_results.py "%RESULTS_DIR%\output.xml" "%RESULTS_DIR%"
exit /b %RC%
