@echo off
REM DEX Archiver - Run decentralized exchanges archive (Hyperliquid + future DEX)
REM Part of parallel archiving system

echo ======================================
echo  DEX ARCHIVER
echo ======================================
echo.

REM Activate Nexus conda environment
call conda activate Nexus

REM Run the DEX archiver
python src\archiver\dex_archiver.py

REM Show exit status
if %errorlevel% equ 0 (
    echo.
    echo ✅ DEX archive completed successfully
) else (
    echo.
    echo ❌ DEX archive failed with error code %errorlevel%
)

echo.
echo Press any key to close...
pause >nul
