@echo off
REM Crypto CEX Archiver - Run centralized exchanges archive
REM Part of parallel archiving system

echo ======================================
echo  CRYPTO CEX ARCHIVER
echo ======================================
echo.

REM Activate Nexus conda environment
call conda activate Nexus

REM Run the crypto CEX archiver
python src\archiver\crypto_cex_archiver.py

REM Show exit status
if %errorlevel% equ 0 (
    echo.
    echo ✅ Crypto CEX archive completed successfully
) else (
    echo.
    echo ❌ Crypto CEX archive failed with error code %errorlevel%
)

echo.
echo Press any key to close...
pause >nul
