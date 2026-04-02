@echo off
REM Daily OHLCV Archiver - Run this manually or schedule with Task Scheduler
REM Runs 3 parallel archivers: CEX Crypto, Stocks, DEX (WAL mode enabled)

echo ================================================================================
echo Daily OHLCV Archive - Starting Parallel Archivers...
echo ================================================================================
echo.
echo Starting 3 parallel processes:
echo   1. Crypto CEX (Binance, Bybit, OKX, MEXC, Phemex, KuCoin, Bitget, Gate.io, Coinbase)
echo   2. Stocks (YFinance)  
echo   3. DEX (Hyperliquid + future DEX sources)
echo.
echo Database: nexus_archive.db (WAL mode - concurrent writes safe)
echo Estimated runtime: ~8 hours (3x faster than sequential)
echo.
echo ================================================================================
echo.

cd /d "C:\Users\Warshawski\nexus_archiver"

REM Activate conda environment
call C:\Users\Warshawski\anaconda3\Scripts\activate.bat Nexus

REM Launch all 3 archivers in parallel
start "Crypto CEX Archive" /MIN cmd /c "python src\archiver\crypto_cex_archiver.py"
timeout /t 2 /nobreak >nul

start "Stocks Archive" /MIN cmd /c "python src\archiver\stocks_archiver.py"
timeout /t 2 /nobreak >nul

start "DEX Archive" /MIN cmd /c "python src\archiver\dex_archiver.py"

echo.
echo ✅ All 3 archivers launched in background
echo.
echo Monitor progress in Task Manager or check log files
echo This window will close in 10 seconds...
echo.
timeout /t 10

exit
