@echo off
REM Cleanup Script - Remove Unnecessary Files
REM Run this to clean up duplicate and debug files

echo ============================================================
echo CLEANUP - Removing Unnecessary Files
echo ============================================================
echo.

REM Remove duplicate app files
if exist app.py (
    del /F app.py
    echo Removed: app.py
)

if exist app_standalone.py (
    del /F app_standalone.py
    echo Removed: app_standalone.py
)

REM Remove duplicate test files
if exist simple_test.py (
    del /F simple_test.py
    echo Removed: simple_test.py
)

if exist test_api.py (
    del /F test_api.py
    echo Removed: test_api.py
)

if exist test_working.py (
    del /F test_working.py
    echo Removed: test_working.py
)

if exist test_detailed.py (
    del /F test_detailed.py
    echo Removed: test_detailed.py
)

REM Remove debug files
if exist inspect_orders.py (
    del /F inspect_orders.py
    echo Removed: inspect_orders.py
)

if exist reproduce_pandas.py (
    del /F reproduce_pandas.py
    echo Removed: reproduce_pandas.py
)

if exist restart_server.py (
    del /F restart_server.py
    echo Removed: restart_server.py
)

REM Remove redundant documentation
if exist QUICKSTART.md (
    del /F QUICKSTART.md
    echo Removed: QUICKSTART.md
)

if exist API_USAGE.md (
    del /F API_USAGE.md
    echo Removed: API_USAGE.md
)

if exist WORKING_SOLUTION.md (
    del /F WORKING_SOLUTION.md
    echo Removed: WORKING_SOLUTION.md
)

if exist SETUP_COMPLETE.md (
    del /F SETUP_COMPLETE.md
    echo Removed: SETUP_COMPLETE.md
)

if exist RESTART.md (
    del /F RESTART.md
    echo Removed: RESTART.md
)

if exist USE_STANDALONE.md (
    del /F USE_STANDALONE.md
    echo Removed: USE_STANDALONE.md
)

REM Remove output files
if exist debug_output.txt (
    del /F debug_output.txt
    echo Removed: debug_output.txt
)

if exist test_output.txt (
    del /F test_output.txt
    echo Removed: test_output.txt
)

if exist test_result.txt (
    del /F test_result.txt
    echo Removed: test_result.txt
)

echo.
echo ============================================================
echo Cleanup Complete!
echo ============================================================
echo.
echo Essential files kept:
echo   - app_debug.py (main server)
echo   - run_me.py (quick start)
echo   - start_all.py (complete setup)
echo   - test_final.py (API test)
echo   - README.md (documentation)
echo   - All folders (api/, services/, models/, etc.)
echo.
echo You can now delete this cleanup.bat file if you want.
echo.
pause
