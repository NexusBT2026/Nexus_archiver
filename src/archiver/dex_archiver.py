"""
DEX Archiver - Archives decentralized exchange data (Hyperliquid + future DEX).
Part of parallel archiving system (runs alongside crypto CEX & stocks archivers).

Future DEX sources to add:
- Uniswap (via The Graph API)
- PancakeSwap (via The Graph API)
- Raydium (via Solana RPC)
- Curve Finance (via The Graph API)
- dYdX (via dYdX API)
- GMX (via The Graph API)
- Alternative data providers: Dune Analytics, Flipside Crypto
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.archiver.comprehensive_archiver import ComprehensiveArchiver
import asyncio


async def run_dex_archive():
    """Archive ONLY DEX data (currently Hyperliquid)."""
    
    archiver = ComprehensiveArchiver()
    
    print("=" * 80)
    print(f"🌐 DEX ARCHIVE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("📝 WAL mode enabled - safe for parallel execution\n")
    
    # Define DEX exchanges (currently only Hyperliquid, expand as needed)
    DEX_EXCHANGES = ['hyperliquid']
    
    # Auto-discover symbols
    print("🔍 Auto-discovering DEX symbols from markets_info/...")
    all_symbols = archiver.discover_all_symbols()
    
    # Filter to only DEX exchanges
    dex_symbols = {ex: syms for ex, syms in all_symbols.items() if ex in DEX_EXCHANGES}
    
    if not dex_symbols:
        print("⚠️  No DEX symbols found. Check markets_info/hyperliquid/ directory.")
        return 1
    
    total_symbols = sum(len(syms) for syms in dex_symbols.values())
    print(f"✅ Found {total_symbols} DEX symbols across {len(dex_symbols)} exchanges\n")
    
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
    
    # Archive all DEX exchanges
    completed = 0
    successful = 0
    start_time = datetime.now()
    
    for exchange, symbols in dex_symbols.items():
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
    print(f"\n✅ DEX Archive complete!")
    print(f"   Success: {successful}/{completed} ({successful/completed*100:.1f}%)")
    print(f"   Time: {elapsed_total:.1f} minutes")
    
    print("\n💡 FUTURE DEX SOURCES TO ADD:")
    print("   - Uniswap (The Graph API)")
    print("   - PancakeSwap (The Graph API)")
    print("   - Raydium (Solana RPC)")
    print("   - Curve Finance (The Graph API)")
    print("   - dYdX (dYdX API)")
    print("   - GMX (The Graph API)")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_dex_archive())
    sys.exit(exit_code)
