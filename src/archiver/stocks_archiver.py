"""
Stocks Archiver - Archives traditional stock/ETF data (YFinance only).
Part of parallel archiving system (runs alongside crypto CEX & DEX archivers).
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.archiver.comprehensive_archiver import ComprehensiveArchiver
import asyncio


async def run_stocks_archive():
    """Archive ONLY YFinance stock/ETF data."""
    
    archiver = ComprehensiveArchiver()
    
    print("=" * 80)
    print(f"📈 STOCKS ARCHIVE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("📝 WAL mode enabled - safe for parallel execution\n")
    
    # Define stocks exchange
    STOCKS_EXCHANGES = ['yfinance']
    
    # Auto-discover symbols
    print("🔍 Auto-discovering stock/ETF symbols from markets_info/...")
    all_symbols = archiver.discover_all_symbols()
    
    # Filter to only YFinance
    stocks_symbols = {ex: syms for ex, syms in all_symbols.items() if ex in STOCKS_EXCHANGES}
    
    if not stocks_symbols:
        print("⚠️  No stock symbols found. Check markets_info/yfinance/ directory.")
        return 1
    
    total_symbols = sum(len(syms) for syms in stocks_symbols.values())
    print(f"✅ Found {total_symbols} stock/ETF symbols\n")
    
    # Load timeframes from config
    config_path = Path(__file__).parent.parent.parent / "archived_data" / "archive_config.json"
    if config_path.exists():
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
            timeframes = config.get('timeframes_to_archive', ["1m", "5m", "15m", "1h", "4h", "1d"])
            fetch_limit = config.get('fetch_limit', 1500)
            progress_every = config.get('progress_update_every', 50)
    else:
        timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        fetch_limit = 1500
        progress_every = 50
    
    total_tasks = total_symbols * len(timeframes)
    print(f"📊 Archiving {total_tasks} combinations")
    print(f"   ({total_symbols} symbols × {len(timeframes)} timeframes)\n")
    
    # Archive YFinance
    completed = 0
    successful = 0
    start_time = datetime.now()
    
    for exchange, symbols in stocks_symbols.items():
        print(f"\n📡 {exchange} ({len(symbols)} symbols)...")
        
        for i, symbol in enumerate(symbols, 1):
            for timeframe in timeframes:
                success = await archiver.archive_symbol(exchange, symbol, timeframe, limit=fetch_limit)
                completed += 1
                if success:
                    successful += 1
            
            if i % progress_every == 0:
                progress = (completed / total_tasks) * 100
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                print(f"   {i}/{len(symbols)} symbols ({progress:.1f}% overall, {elapsed:.1f}min elapsed)")
        
        print(f"   ✅ Completed {exchange}")
    
    # Final stats
    elapsed_total = (datetime.now() - start_time).total_seconds() / 60
    print(f"\n✅ Stocks Archive complete!")
    print(f"   Success: {successful}/{completed} ({successful/completed*100:.1f}%)")
    print(f"   Time: {elapsed_total:.1f} minutes")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_stocks_archive())
    sys.exit(exit_code)
