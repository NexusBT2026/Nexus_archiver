# Nexus Archiver

A standalone, open-source OHLCV (Open, High, Low, Close, Volume) data archiving system that supports multiple cryptocurrency exchanges and traditional stock/ETF markets, building long-term historical datasets.

## Features

- **Multi-Exchange Support**: Binance, Bybit, OKX, MEXC, Phemex, Hyperliquid, Coinbase, KuCoin, Bitget, Gate.io
- **Stock & ETF Markets**: Yahoo Finance integration with 11,000+ symbols (US stocks, ETFs, mutual funds)
- **Live Market Refresh**: Symbol lists are fetched from live exchange APIs at archiver startup — always current, no stale caches
- **Per-Exchange Timeframe Filtering**: Each exchange only archives timeframes it actually supports — no more invalid timeframe errors
- **Parallel Archiving**: Three independent archivers (CEX crypto, DEX/Hyperliquid, Stocks) run simultaneously
- **Incremental Updates**: Only fetches new candles, avoiding redundant API calls
- **Smart Rate Limiting**: Built-in token bucket rate limiting to respect API limits
- **Retention Management**: Configurable retention policies to prevent disk bloat
- **Progress Tracking**: Real-time progress monitoring for large batch operations
- **Disk Space Monitoring**: Automatic monitoring to prevent storage issues
- **Async Operations**: Efficient asynchronous data fetching

## Project Structure

```
nexus_archiver/
├── src/
│   ├── archiver/              # Main archiver modules
│   │   ├── comprehensive_archiver.py  # Archives ALL symbols from ALL exchanges
│   │   ├── crypto_cex_archiver.py     # CEX crypto (Binance, Bybit, OKX, etc.)
│   │   ├── dex_archiver.py            # DEX crypto (Hyperliquid)
│   │   ├── stocks_archiver.py         # Stocks & ETFs (Yahoo Finance)
│   │   ├── daily_ohlcv_archiver.py    # Daily incremental archiving
│   │   └── __init__.py
│   ├── data/                  # Exchange data source implementations
│   │   ├── binance_ohlcv_source.py
│   │   ├── bybit_ohlcv_source.py
│   │   ├── okx_ohlcv_source.py
│   │   ├── mexc_ohlcv_source.py
│   │   ├── phemex_ohlcv_source.py
│   │   ├── hyperliquid_ohlcv_source.py
│   │   ├── coinbase_ohlcv_source.py
│   │   ├── kucoin_ohlcv_source.py
│   │   ├── bitget_ohlcv_source.py
│   │   ├── gateio_ohlcv_source.py
│   │   ├── yfinance_ohlcv_source.py   # Yahoo Finance (stocks/ETFs)
│   │   ├── market_refresher.py        # Live market refresh at startup
│   │   └── __init__.py
│   ├── utils/                 # Utility modules
│   │   └── token_bucket.py    # Rate limiting implementation
│   ├── exchange/              # Exchange configuration
│   │   └── config.py          # Configuration loader
│   └── __init__.py
├── archived_data/             # Archived OHLCV data storage
│   └── archive_config.json    # Archiver configuration
├── markets_info/              # Market info — auto-refreshed at startup
│   ├── binance/
│   ├── bybit/
│   ├── okx/
│   ├── mexc/
│   ├── bitget/
│   ├── gateio/
│   ├── kucoin/
│   ├── phemex/
│   ├── coinbase/
│   ├── hyperliquid/
│   └── yfinance/
├── config.json.example        # Example configuration file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Requirements

- **Python 3.8, 3.9, 3.10, 3.11, or 3.12+** (all supported)

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/nexus_archiver.git
cd nexus_archiver
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Copy the example configuration and add your API keys:

```bash
Copy-Item config.json.example config.json
```

Edit `config.json` with your exchange API credentials. **Note**: For public OHLCV data, API keys are optional for most exchanges.

```json
{
  "binance_api_key": "YOUR_BINANCE_API_KEY",
  "binance_api_secret": "YOUR_BINANCE_API_SECRET",
  "bybit_api_key": "YOUR_BYBIT_API_KEY",
  "bybit_api_secret": "YOUR_BYBIT_API_SECRET",
  ...
}
```

## Usage

### Parallel Archiving (Recommended)

Run all three archivers simultaneously for maximum throughput. Each writes to the same SQLite database safely via WAL mode.

**Windows — open three terminals:**

```bat
# Terminal 1 — CEX crypto (Binance, Bybit, OKX, MEXC, Bitget, Gate.io, KuCoin, Phemex, Coinbase)
run_crypto_cex_archive.bat

# Terminal 2 — DEX (Hyperliquid perpetuals)
run_dex_archive.bat

# Terminal 3 — Stocks & ETFs (Yahoo Finance)
run_stocks_archive.bat
```

At startup each archiver automatically refreshes symbol lists from live exchange APIs, so you always archive current markets — no need to manually update `markets_info/`.

### Manual Refresh of Market Symbols

To refresh all symbol lists without running the full archiver:

```bash
python -m src.data.market_refresher
```

Or refresh a specific exchange:

```python
from src.data.market_refresher import refresh_all_markets
refresh_all_markets(exchanges=['bybit', 'kucoin'])
```

### Daily Archiver (Incremental Updates)

Run this daily to continuously accumulate historical data:

```python
from src.archiver.daily_ohlcv_archiver import OHLCVArchiver

archiver = OHLCVArchiver(db_path="archived_data/nexus_archive.db")

# Archive specific symbols
await archiver.archive_symbol(
    exchange='binance',
    symbol='BTC/USDT',
    timeframes=['1h', '4h', '1d']
)

# Or archive multiple symbols
symbols = [
    ('binance', 'BTC/USDT'),
    ('binance', 'ETH/USDT'),
    ('bybit', 'BTC/USDT'),
]
await archiver.archive_multiple(symbols, timeframes=['1h', '4h', '1d'])
```

### Comprehensive Archiver (Auto-Discovery)

Archives ALL symbols from ALL exchanges automatically:

```python
from src.archiver.comprehensive_archiver import ComprehensiveArchiver

archiver = ComprehensiveArchiver()

# Archive everything
await archiver.archive_all_exchanges()

# Or archive specific exchange
await archiver.archive_exchange('binance')
```

## Automation with Task Scheduler

### Windows Task Scheduler Setup

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Name: "Daily OHLCV Archive"
4. Trigger: Daily at 2:00 AM
5. Action: Start a Program
   - Program: `C:\Users\Warshawski\nexus_archiver\venv\Scripts\python.exe`
   - Arguments: `run_archiver.py`
   - Start in: `C:\Users\Warshawski\nexus_archiver`
6. Finish and test

## Configuration

### Archive Configuration

Edit `archived_data/archive_config.json`:

```json
{
  "timeframes_to_archive": ["1h", "4h", "1d"],
  "fetch_limit": 1500,
  "progress_update_every": 50,
  "retention_note": "See RETENTION_POLICIES in code"
}
```

### Retention Policies

Configured in `comprehensive_archiver.py`:

- **1m**: 3 months
- **5m**: 6 months
- **15m**: 12 months
- **1h**: 24 months
- **4h**: 36 months
- **1d**: 60 months
- **1w**: Forever

## Data Storage

Data is stored in SQLite database at `archived_data/nexus_archive.db`:

- **Format**: SQLite3
- **Compression**: Efficient storage (~50 bytes per candle)
- **Indexing**: Optimized for fast queries by symbol, timeframe, and timestamp

## API Rate Limiting

Built-in token bucket rate limiting per exchange (verified rates):

| Exchange | Rate | Notes |
|---|---|---|
| Binance | 10 req/s | |
| Bybit | 10 req/s | |
| OKX | 10 req/s | |
| MEXC | 5 req/s | |
| Bitget | 10 req/s | |
| Gate.io | 10 req/s | |
| KuCoin | 10 req/s | |
| Phemex | 10 req/s | |
| Coinbase | 29 req/s | |
| Hyperliquid | 10 req/s | |
| Yahoo Finance | 2 req/s | Free, no key required |

## Troubleshooting

### Import Errors

Ensure you're running from the project root:

```bash
cd C:\Users\Warshawski\nexus_archiver
python run_archiver.py
```

### API Key Issues

- Public OHLCV data doesn't require API keys for most exchanges
- Check `config.json` for correct credentials
- Verify API keys have proper permissions

### Database Locked

The archive database uses WAL (Write-Ahead Logging) mode, so all three archivers can safely run in parallel without locking conflicts.

## Development

### Adding New Exchange

1. Create new data source in `src/data/` (e.g., `new_exchange_ohlcv_source.py`)
2. Implement `fetch_historical_data()` method
3. Add to exchange_sources dict in archiver
4. Update `config.json.example` with API keys

### Testing

```bash
# Test single symbol archive
python -c "import asyncio; from src.archiver.daily_ohlcv_archiver import OHLCVArchiver; asyncio.run(OHLCVArchiver().archive_symbol('binance', 'BTC/USDT', ['1h']))"
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Support

For issues or questions, please open an issue in the repository.

---

**Note**: This is a standalone extraction from a larger trading system. It focuses purely on data archiving functionality.
