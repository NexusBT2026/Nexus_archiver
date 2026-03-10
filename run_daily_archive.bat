@echo off
REM Daily OHLCV Archiver - Run this manually or schedule with Task Scheduler
REM This batch file activates the Nexus environment and runs the archiver

echo ================================================================================
echo Daily OHLCV Archive - Starting...
echo ================================================================================
echo.

cd /d "C:\Users\Warshawski\nexus_archiver"

REM Activate conda environment and run archiver
call C:\Users\Warshawski\anaconda3\Scripts\activate.bat Nexus

python src\archiver\comprehensive_archiver.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Script failed with exit code %ERRORLEVEL%
    echo Check the output above for details
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ================================================================================
echo Archive complete. Window will close in 10 seconds...
echo ================================================================================
timeout /t 10

exit
