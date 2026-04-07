"""
Crypto CEX Archiver - Archives centralized exchange crypto data only.
Part of parallel archiving system (runs alongside stocks & DEX archivers).
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.archiver.comprehensive_archiver import ComprehensiveArchiver
from src.data.market_refresher import refresh_all_markets
import asyncio


async def run_crypto_cex_archive():
    """Archive ONLY centralized exchange crypto data."""
    
    archiver = ComprehensiveArchiver()
    
    print("=" * 80)
    print(f"💱 CRYPTO CEX ARCHIVE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("📝 WAL mode enabled - safe for parallel execution\n")
    
    # Define CEX exchanges only (exclude yfinance and hyperliquid)
    CEX_EXCHANGES = ['binance', 'bybit', 'okx', 'mexc', 'phemex', 'kucoin', 'bitget', 'gateio', 'coinbase']
    
    # Refresh markets before discovery so symbol lists are current
    refresh_all_markets(exchanges=CEX_EXCHANGES)

    # Auto-discover symbols
    print("🔍 Auto-discovering CEX symbols from markets_info/...")
    all_symbols = archiver.discover_all_symbols()
    
    # Filter to only CEX exchanges
    cex_symbols = {ex: syms for ex, syms in all_symbols.items() if ex in CEX_EXCHANGES}
    
    if not cex_symbols:
        print("⚠️  No CEX symbols found. Check markets_info/ directory.")
        return 1
    
    # Sort by priority
    exchange_symbols = {}
    for exchange in archiver.EXCHANGE_PRIORITY:
        if exchange in cex_symbols:
            exchange_symbols[exchange] = cex_symbols[exchange]
    
    total_symbols = sum(len(syms) for syms in exchange_symbols.values())
    print(f"✅ Found {total_symbols} CEX symbols across {len(exchange_symbols)} exchanges\n")
    
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
    
    # Archive all CEX exchanges
    completed = 0
    successful = 0
    start_time = datetime.now()
    
    for exchange, symbols in exchange_symbols.items():
        # Filter to timeframes supported by this exchange
        source_class = archiver.exchange_sources.get(exchange)
        if source_class and hasattr(source_class, 'get_available_timeframes'):
            supported = set(source_class().get_available_timeframes())
            exchange_tfs = [tf for tf in timeframes if tf in supported]
        else:
            exchange_tfs = timeframes
        print(f"\n📡 {exchange} ({len(symbols)} symbols, {len(exchange_tfs)}/{len(timeframes)} timeframes)...")
        
        for i, symbol in enumerate(symbols, 1):
            for timeframe in exchange_tfs:
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
    print(f"\n✅ CEX Archive complete!")
    print(f"   Success: {successful}/{completed} ({successful/completed*100:.1f}%)")
    print(f"   Time: {elapsed_total:.1f} minutes")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_crypto_cex_archive())
    sys.exit(exit_code)
