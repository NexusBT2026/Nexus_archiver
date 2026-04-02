# Parallel Archiving System

## Overview
The archiver is split into 3 independent processes that run in parallel, all writing to the same database using SQLite WAL mode for concurrent access.

## Architecture

### Database Configuration
- **WAL Mode**: `PRAGMA journal_mode=WAL` enables multiple concurrent writers
- **Busy Timeout**: `PRAGMA busy_timeout=30000` (30 seconds) prevents lock errors
- **Connection Timeout**: All `sqlite3.connect()` calls use `timeout=30.0`

### The 3 Parallel Archivers

#### 1. Crypto CEX Archiver (`crypto_cex_archiver.py`)
**Exchanges**: Binance, Bybit, OKX, MEXC, Phemex, KuCoin, Bitget, Gate.io, Coinbase

**Symbol Count**: ~1,500 crypto trading pairs

**Estimated Tasks**: 1,500 symbols × 15 timeframes = 22,500 API calls

**Runtime**: ~8 hours

**Launcher**: `run_crypto_cex_archive.bat`

#### 2. Stocks Archiver (`stocks_archiver.py`)
**Exchanges**: YFinance only

**Symbol Count**: ~2,070 stocks/ETFs

**Estimated Tasks**: 2,070 symbols × 15 timeframes = 31,050 API calls

**Runtime**: ~8 hours  

**Launcher**: `run_stocks_archive.bat`

#### 3. DEX Archiver (`dex_archiver.py`)
**Exchanges**: Hyperliquid (currently)

**Symbol Count**: ~229 perpetual contracts

**Estimated Tasks**: 229 symbols × 15 timeframes = 3,435 API calls

**Runtime**: ~1 hour

**Launcher**: `run_dex_archive.bat`

**Future Expansion**: See [DEX_SOURCES.md](DEX_SOURCES.md) for planned additions

## Usage

### Quick Start (Parallel Execution)
```batch
run_parallel_archive.bat
```
This launches all 3 archivers in separate windows simultaneously.

### Individual Execution
```batch
run_crypto_cex_archive.bat    # CEX crypto only
run_stocks_archive.bat         # Stocks/ETFs only
run_dex_archive.bat           # DEX/perpetuals only
```

### Scheduling (Windows Task Scheduler)
Schedule all 3 batch files to run daily at the same time (e.g., 2:00 AM).

**Important**: Ensure all 3 tasks run with the same user account to avoid permission issues.

## Performance Comparison

| Mode | Runtime | Speedup |
|------|---------|---------|
| Sequential (old) | ~24 hours | Baseline |
| Parallel (new) | ~8 hours | 3x faster |

## Data Integrity

### Concurrent Access Safety
- **Multiple Writers**: WAL mode supports multiple processes writing simultaneously
- **Read-While-Write**: Your backtesting system can read data while archivers are running
- **No Overwrites**: `INSERT OR IGNORE` ensures existing data is never overwritten
- **Automatic Pruning**: Old data beyond retention policies is automatically deleted

### Retention Policies
| Timeframe | Max Age | Max Candles |
|-----------|---------|-------------|
| 1m | 3 months | ~130,000 |
| 5m | 6 months | ~52,000 |
| 15m | 12 months | ~35,000 |
| 1h | 24 months | ~17,500 |
| 4h | 36 months | ~6,500 |
| 1d | 60 months | ~1,800 |
| 1w | Forever | Unlimited |

### Data Quality Verified
- **MEXC**: 100% complete, 80K+ candles, zero gaps
- **Hyperliquid**: 97.8% complete, 126K+ candles, 3 minor gaps (exchange downtime)
- **Binance**: 100% complete, 1,463 hourly candles

## Database Locks Issue (SOLVED)

### Problem
Before WAL mode, the database used `journal_mode=delete` which only allows ONE writer at a time. This caused:
- ❌ "database is locked" errors when backtesting system tried to read during archiving
- ❌ Cannot run multiple archivers in parallel
- ❌ Long sequential runtime (~24 hours)

### Solution  
WAL mode (`journal_mode=wal`) enables:
- ✅ Multiple concurrent writers (all 3 archivers simultaneously)
- ✅ Read-while-write (backtesting reads while archiving writes)
- ✅ No lock errors with 30-second busy timeout
- ✅ 3x faster total runtime

## Testing Concurrent Access

### Simple Test
```batch
python test_concurrent_writes.py
```
Performs 20 test writes and verifies no lock errors.

### Comprehensive Test
```batch
python test_wal_mode.py
```
Spawns 2 writers + 1 reader in parallel threads to simulate real concurrent access.

## Troubleshooting

### "Database is locked" error
1. Check journal mode: `python -c "import sqlite3; conn = sqlite3.connect('archived_data/nexus_archive.db'); print(conn.execute('PRAGMA journal_mode').fetchone()[0])"`
2. Should return `wal` - if not, re-run any archiver once to activate WAL mode
3. Check for stale locks: Delete `nexus_archive.db-wal` and `nexus_archive.db-shm` files if present

### Archiver crashes or hangs
- Check API rate limits in config (too aggressive limits cause 429 errors)
- Verify conda environment is activated (`conda activate Nexus`)
- Check disk space (WAL files can grow during heavy writes)

### Missing data
- Retention policies automatically delete old data
- Run archivers daily to maintain continuous history
- Some exchanges have downtime causing gaps (normal)

## Configuration

All 3 archivers read from `archived_data/archive_config.json`:

```json
{
  "timeframes_to_archive": ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"],
  "fetch_limit": 1500,
  "progress_update_every": 50
}
```

## Symbol Discovery

Symbols are automatically discovered from `markets_info/` directories:
- `markets_info/binance/binance_markets_loads_data_bot.json`
- `markets_info/yfinance/yfinance_symbols_data_bot.json`
- `markets_info/hyperliquid/hyperliquid_symbols_meta_data_bot.json`
- ... (one per exchange)

No manual symbol configuration needed.

## Future Enhancements

### DEX/DeFi Sources to Add
See [DEX_SOURCES.md](DEX_SOURCES.md) for detailed list of planned decentralized data sources:
- Uniswap, PancakeSwap, Raydium (DEX spot)
- Curve Finance (stablecoin pools)
- dYdX, GMX (decentralized perpetuals)
- Alternative providers: The Graph, Dune Analytics, Flipside Crypto

### Potential 4th Archiver
If DEX sources expand significantly, consider splitting:
- **dex_spot_archiver.py**: Uniswap, PancakeSwap, Raydium, Curve
- **dex_perp_archiver.py**: Hyperliquid, dYdX, GMX

## Technical Notes

### Why 3 Archivers?
- **Asset Class Separation**: CEX crypto, traditional stocks, DEX have different market hours and characteristics
- **Independent Failures**: If one archiver fails, others continue
- **Balanced Load**: Each archiver takes roughly the same time (~8 hours)
- **Easy Scheduling**: Can schedule different times if needed (e.g., stocks during market hours)

### Why Same Database?
- **Unified Data Access**: Backtesting queries can span multiple sources
- **Simplified Management**: One database to backup/maintain
- **Efficient Storage**: Shared indexes and metadata tables
- **Cross-Exchange Analysis**: Easy to compare symbols across exchanges

### WAL Mode Details
- Creates `nexus_archive.db-wal` (write-ahead log) and `nexus_archive.db-shm` (shared memory) files
- WAL file grows during writes, checkpointed automatically
- Safe to delete WAL/SHM files when NO processes are accessing database
- Performance: Faster writes, slightly slower reads (negligible for time-series data)

## System Requirements
- **RAM**: 4GB minimum (8GB recommended for parallel execution)
- **Disk**: 50GB+ free space (database + WAL files)
- **CPU**: Multi-core recommended (each archiver uses 1-2 cores)
- **Network**: Stable high-speed connection (APIs rate-limited, not bandwidth-limited)
