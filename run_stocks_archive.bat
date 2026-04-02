@echo off
REM Stocks Archiver - Run YFinance stock/ETF archive
REM Part of parallel archiving system

echo ======================================
echo  STOCKS ARCHIVER
echo ======================================
echo.

REM Activate Nexus conda environment
call conda activate Nexus

REM Run the stocks archiver
python src\archiver\stocks_archiver.py

REM Show exit status
if %errorlevel% equ 0 (
    echo.
    echo ✅ Stocks archive completed successfully
) else (
    echo.
    echo ❌ Stocks archive failed with error code %errorlevel%
)

echo.
echo Press any key to close...
pause >nul
