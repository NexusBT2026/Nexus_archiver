"""
Comprehensive OHLCV Archiver - Archives ALL symbols from ALL exchanges automatically.

Auto-discovers 1769+ symbols from markets_info/ and archives them daily with:
- Configurable retention policies (prevent disk bloat)
- Incremental updates (only fetch new candles)
- Disk space monitoring
- Progress tracking for large batches

Storage: ~50 bytes/candle = ~26.5 GB for full archive (manageable)
"""

import sqlite3
import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.binance_ohlcv_source import BinanceOHLCVDataSource
from src.data.bybit_ohlcv_source import BybitOHLCVDataSource
from src.data.okx_ohlcv_source import OKXOHLCVDataSource
from src.data.mexc_ohlcv_source import MEXCOHLCVDataSource
from src.data.phemex_ohlcv_source import PhemexOHLCVDataSource
from src.data.hyperliquid_ohlcv_source import HyperliquidOHLCVDataSource
from src.data.coinbase_ohlcv_source import CoinbaseOHLCVDataSource
from src.data.kucoin_ohlcv_source import KucoinOHLCVDataSource
from src.data.bitget_ohlcv_source import BitgetOHLCVDataSource
from src.data.gateio_ohlcv_source import GateioOHLCVDataSource
from src.data.yfinance_ohlcv_source import YFinanceOHLCVDataSource

from src.utils.token_bucket import TokenBucket


class ComprehensiveArchiver:
    """Archive ALL symbols from ALL exchanges with retention management."""
    
    # Retention policies: keep last N months per timeframe to manage disk space
    RETENTION_POLICIES = {
        '1m': 3,      # 1-minute: 3 months (~130k candles)
        '5m': 6,      # 5-minute: 6 months (~52k candles)
        '15m': 12,    # 15-minute: 1 year (~35k candles)
        '1h': 24,     # 1-hour: 2 years (~17.5k candles)
        '4h': 36,     # 4-hour: 3 years (~6.5k candles)
        '1d': 60,     # Daily: 5 years (~1.8k candles)
        '1w': None,   # Weekly: keep forever (~260 candles/year)
    }
    
    # Exchange-specific max limits from pagination test results
    MAX_LIMITS = {
        'hyperliquid': 5000,  # Can get 5k+ candles!
        'mexc': 2000,
        'binance': 1500,
        'bybit': 1000,
        'bitget': 1000,
        'gateio': 1000,
        'phemex': 1000,
        'okx': 300,
        'coinbase': 300,
        'kucoin': 200,
    }
    
    # Exchange priority order: Hyperliquid first (best data), then others
    EXCHANGE_PRIORITY = [
        'yfinance',     # 20k candles - stocks/ETFs only
        'hyperliquid',  # 5k candles - BEST
        'mexc',         # 2k candles
        'binance',      # 1.5k candles
        'phemex',       # 1k candles
        'bybit',        # 1k candles
        'gateio',       # 1k candles
        'bitget',       # 1k candles
        'okx',          # 300 candles
        'coinbase',     # 300 candles
        'kucoin',       # 200 candles
    ]
    
    def __init__(self, db_path="archived_data/nexus_archive.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
        
        # Exchange source mapping
        self.exchange_sources = {
            'yfinance': YFinanceOHLCVDataSource,
            'binance': BinanceOHLCVDataSource,
            'bybit': BybitOHLCVDataSource,
            'okx': OKXOHLCVDataSource,
            'mexc': MEXCOHLCVDataSource,
            'phemex': PhemexOHLCVDataSource,
            'hyperliquid': HyperliquidOHLCVDataSource,
            'coinbase': CoinbaseOHLCVDataSource,
            'kucoin': KucoinOHLCVDataSource,
            'bitget': BitgetOHLCVDataSource,
            'gateio': GateioOHLCVDataSource,
        }
        
        # Token bucket rate limiters (exchange-specific)
        # NOTE: Hyperliquid uses 60% capacity (trading bot already using 40%)
        self.exchange_buckets = {
            'phemex': TokenBucket(100, 8.3, "Phemex", False, 60),                 # CCXT: 120.5ms = 8.30 req/sec (VERIFIED)
            'hyperliquid': TokenBucket(60, 6.0, "Hyperliquid", False, 60),        # 60% of official: 100 capacity, 10 refill/sec (bot uses 40%)
            'coinbase': TokenBucket(100, 29.41, "Coinbase", False, 60),           # CCXT: 34ms = 29.41 req/sec (VERIFIED)
            'binance': TokenBucket(100, 20.0, "Binance", False, 60),              # CCXT: 50ms = 20.00 req/sec (VERIFIED)
            'kucoin': TokenBucket(100, 100.0, "KuCoin", False, 60),               # CCXT: 10ms = 100.00 req/sec (VERIFIED) ⚠️ FASTEST!
            'bybit': TokenBucket(100, 50.0, "Bybit", False, 60),                  # CCXT: 20ms = 50.00 req/sec (VERIFIED 2026-01-03)
            'okx': TokenBucket(100, 9.09, "OKX", False, 60),                      # CCXT: 110ms = 9.09 req/sec (VERIFIED 2026-01-03)
            'bitget': TokenBucket(100, 20.0, "Bitget", False, 60),                # CCXT: 50ms = 20.00 req/sec (VERIFIED 2026-01-03)
            'gateio': TokenBucket(100, 20.0, "Gateio", False, 60),                # CCXT: 50ms = 20.00 req/sec (VERIFIED 2026-01-03)
            'mexc': TokenBucket(100, 20.0, "MEXC", False, 60),                    # CCXT: 50ms = 20.00 req/sec (VERIFIED 2026-01-03)
            'yfinance': TokenBucket(100, 2.0, "YFinance", False, 60),             # Free API: conservative 2 req/sec to avoid blocks
        }
    
    def _ensure_db_directory(self):
        """Create archived_data directory."""
        Path(self.db_path).parent.mkdir(exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database with WAL mode for concurrent writes."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # Enable WAL mode for concurrent access (multiple archivers writing simultaneously)
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
        
        # OHLCV data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv_data (
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                PRIMARY KEY (exchange, symbol, timeframe, timestamp)
            )
        """)
        
        # Metadata tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fetch_metadata (
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                last_timestamp INTEGER NOT NULL,
                last_fetch_date TEXT NOT NULL,
                total_candles INTEGER DEFAULT 0,
                PRIMARY KEY (exchange, symbol, timeframe)
            )
        """)
        
        # Performance index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query 
            ON ohlcv_data(exchange, symbol, timeframe, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def get_last_timestamp(self, exchange, symbol, timeframe):
        """Get last stored timestamp for incremental fetching."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT last_timestamp FROM fetch_metadata
            WHERE exchange = ? AND symbol = ? AND timeframe = ?
        """, (exchange, symbol, timeframe))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def store_ohlcv_data(self, exchange, symbol, timeframe, ohlcv_data):
        """Store OHLCV data with duplicate detection."""
        if not ohlcv_data:
            return 0
        
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        inserted = 0
        for candle in ohlcv_data:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO ohlcv_data 
                    (exchange, symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    exchange, symbol, timeframe,
                    candle[0], candle[1], candle[2], candle[3], candle[4], candle[5]
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.IntegrityError:
                continue
        
        # Update metadata
        if ohlcv_data:
            last_timestamp = max(candle[0] for candle in ohlcv_data)
            cursor.execute("""
                INSERT OR REPLACE INTO fetch_metadata
                (exchange, symbol, timeframe, last_timestamp, last_fetch_date, total_candles)
                VALUES (?, ?, ?, ?, ?, 
                    COALESCE((SELECT total_candles FROM fetch_metadata 
                              WHERE exchange = ? AND symbol = ? AND timeframe = ?), 0) + ?)
            """, (
                exchange, symbol, timeframe, last_timestamp, 
                datetime.now().isoformat(),
                exchange, symbol, timeframe, inserted
            ))
        
        conn.commit()
        conn.close()
        
        return inserted
    
    def prune_old_data(self, exchange, symbol, timeframe):
        """Remove old data based on retention policy to manage disk space."""
        retention_months = self.RETENTION_POLICIES.get(timeframe)
        
        if retention_months is None:
            return 0  # Keep forever
        
        cutoff_date = datetime.now() - timedelta(days=retention_months * 30)
        cutoff_timestamp = int(cutoff_date.timestamp() * 1000)
        
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM ohlcv_data
            WHERE exchange = ? AND symbol = ? AND timeframe = ? AND timestamp < ?
        """, (exchange, symbol, timeframe, cutoff_timestamp))
        
        deleted = cursor.rowcount
        
        # Update metadata total count
        if deleted > 0:
            cursor.execute("""
                UPDATE fetch_metadata
                SET total_candles = total_candles - ?
                WHERE exchange = ? AND symbol = ? AND timeframe = ?
            """, (deleted, exchange, symbol, timeframe))
        
        conn.commit()
        conn.close()
        
        return deleted
    
    async def archive_symbol(self, exchange_name, symbol, timeframe, limit=1000):
        """Archive single symbol with smart backfill and token bucket rate limiting."""
        source_class = self.exchange_sources.get(exchange_name.lower())
        if not source_class:
            return False
        
        # TOKEN BUCKET RATE LIMITING: Wait before consuming tokens
        bucket = self.exchange_buckets.get(exchange_name.lower())
        if bucket:
            wait_time = bucket.wait_time(tokens=1)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            bucket.consume(tokens=1)
        
        source = source_class()
        last_timestamp = self.get_last_timestamp(exchange_name, symbol, timeframe)
        is_first_run = last_timestamp is None
        
        try:
            # Hyperliquid uses lookback_days method (not CCXT)
            if exchange_name.lower() == 'hyperliquid':
                # Use 2-year lookback to get maximum available data
                df = source.fetch_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    lookback_days=730  # 2 years
                )
                
                if not df.empty:
                    # Convert DataFrame to OHLCV list format
                    ohlcv_data = []
                    for _, row in df.iterrows():
                        ohlcv_data.append([
                            int(row['timestamp'].timestamp() * 1000),
                            row['open'],
                            row['high'],
                            row['low'],
                            row['close'],
                            row['volume']
                        ])
                    
                    inserted = self.store_ohlcv_data(exchange_name, symbol, timeframe, ohlcv_data)
                    
                    if inserted > 0:
                        self.prune_old_data(exchange_name, symbol, timeframe)
                    
                    return inserted > 0
                    
                return False
            
            # Standard CCXT exchanges: Use exchange-specific max limit on EVERY run
            # This ensures we get as much historical data as possible each time
            limit = self.MAX_LIMITS.get(exchange_name.lower(), 1000)
            
            # CCXT-based data sources provide a sync `fetch_historical_data` method.
            # Call it in an executor to keep archive_symbol async-friendly.
            fetch_symbol = symbol
            ohlcv_data = None
            loop = asyncio.get_event_loop()
            try:
                # If the discovered symbol is a clean base (no slash or dash),
                # generate the fetch symbol using the exact rules from the
                # pipeline (pipeline_BT_unified_async.py#L824-L926).
                if ('/' not in symbol) and ('-' not in symbol):
                    # Phemex: handle u-prefixes for small-cap tokens (based on actual market data)
                    if exchange_name.lower() == 'phemex':
                        u1000000_symbols = {'BABYDOGE', 'MOG'}
                        u10000_symbols = set()  # No u10000 symbols exist in Phemex markets
                        u1000_symbols = {'BONK', 'CAT', 'CHEEMS', 'FLOKI', 'PEPE', 'RATS', 'SATS', 'SHIB', 'WHY', 'XEC'}

                        if symbol in u1000000_symbols:
                            fetch_symbol = f'u1000000{symbol}USDT'
                        elif symbol in u10000_symbols:
                            fetch_symbol = f'u10000{symbol}USDT'
                        elif symbol in u1000_symbols:
                            fetch_symbol = f'u1000{symbol}USDT'
                        else:
                            fetch_symbol = f"{symbol}USDT"

                    # Hyperliquid: some bases require a leading 'k' (based on actual market data)
                    elif exchange_name.lower() == 'hyperliquid':
                        def convert_to_hyperliquid_symbol(base_symbol):
                            k_symbols = {'BONK', 'FLOKI', 'LUNC', 'NEIRO', 'PEPE', 'SHIB'}
                            if base_symbol in k_symbols:
                                return f'k{base_symbol}'
                            return base_symbol

                        fetch_symbol = convert_to_hyperliquid_symbol(symbol)

                    # Coinbase spot uses '-' separator and USDC quote in pipeline
                    elif exchange_name.lower() == 'coinbase':
                        fetch_symbol = f"{symbol}-USDC"

                    # Binance spot uses USDC quote (not USDT)
                    elif exchange_name.lower() == 'binance':
                        fetch_symbol = f"{symbol}/USDC"

                    # KuCoin futures use /USDT:USDT perpetual format
                    elif exchange_name.lower() == 'kucoin':
                        fetch_symbol = f"{symbol}/USDT:USDT"

                    # Perp-style exchanges use BASE/USDT:USDT format for perpetuals
                    elif exchange_name.lower() in {'bybit', 'okx', 'bitget', 'gateio', 'mexc'}:
                        fetch_symbol = f"{symbol}/USDT:USDT"

                    # YFinance uses raw stock symbols (no USDT suffix)
                    elif exchange_name.lower() == 'yfinance':
                        fetch_symbol = symbol

                    else:
                        # Fallback: prefer slash-form then USDT suffix
                        fetch_symbol = f"{symbol}/USDT:USDT"

                    # If the data-source exposes a CCXT exchange with loaded markets,
                    # prefer any candidate that appears in the exchange.market keys
                    exch = getattr(source, 'exchange', None)
                    tmp_df = None
                    try:
                        markets_keys = None
                        if exch is not None:
                            markets = getattr(exch, 'markets', None) or getattr(exch, 'symbols', None) or {}
                            markets_keys = set(markets.keys()) if isinstance(markets, dict) else set(markets)
                    except Exception:
                        markets_keys = None

                    # Build fallback candidate list (pipeline-first then previous candidates)
                    if exchange_name.lower() == 'phemex':
                        # Only include u-prefix variations that actually exist in Phemex markets
                        candidates = [fetch_symbol, f"{symbol}USDT"]
                        # Add u-prefix candidates only for known small-cap tokens
                        if symbol in {'BABYDOGE', 'MOG'}:
                            candidates.append(f"u1000000{symbol}USDT")
                        elif symbol in {'BONK', 'CAT', 'CHEEMS', 'FLOKI', 'PEPE', 'RATS', 'SATS', 'SHIB', 'WHY', 'XEC'}:
                            candidates.append(f"u1000{symbol}USDT")
                    elif exchange_name.lower() == 'coinbase':
                        candidates = [fetch_symbol, f"{symbol}-USDC", f"{symbol}/USDC"]
                    elif exchange_name.lower() == 'binance':
                        candidates = [fetch_symbol, f"{symbol}/USDC", f"{symbol}USDC"]
                    elif exchange_name.lower() == 'kucoin':
                        candidates = [fetch_symbol, f"{symbol}/USDT:USDT", f"{symbol}/USDT", f"{symbol}USDT"]
                    elif exchange_name.lower() in {'bybit', 'okx', 'bitget', 'gateio', 'mexc'}:
                        candidates = [fetch_symbol, f"{symbol}/USDT:USDT", f"{symbol}/USDT", f"{symbol}USDT"]
                    elif exchange_name.lower() == 'yfinance':
                        candidates = [fetch_symbol]
                    else:
                        candidates = [f"{symbol}/USDT", f"{symbol}/USDC", f"{symbol}USDC", f"{symbol}/USDTM", f"{symbol}USDT", f"{symbol}USDTM"]

                    # If markets_keys available, pick the first candidate present and try it directly
                    chosen = None
                    if markets_keys:
                        for c in candidates:
                            if c in markets_keys:
                                chosen = c
                                break
                        if chosen:
                            try:
                                tmp_df = await loop.run_in_executor(
                                    None,
                                    source.fetch_historical_data,
                                    chosen,
                                    timeframe,
                                    min(limit, self.MAX_LIMITS.get(exchange_name.lower(), limit)),
                                    last_timestamp + 1 if last_timestamp else None
                                )
                                fetch_symbol = chosen
                            except Exception:
                                tmp_df = None

                    # If the chosen canonical/markets-backed form failed (or markets not available),
                    # fall back to trying the candidate list sequentially.
                    if tmp_df is None or getattr(tmp_df, 'empty', False):
                        # Candidate fallback list mirrors previous behavior but
                        # preserves the pipeline-first attempt above.
                        if exchange_name.lower() == 'phemex':
                            # Only try u-prefix variations for known small-cap tokens
                            candidates = [f"{symbol}USDT"]
                            if symbol in {'BABYDOGE', 'MOG'}:
                                candidates.append(f"u1000000{symbol}USDT")
                            elif symbol in {'BONK', 'CAT', 'CHEEMS', 'FLOKI', 'PEPE', 'RATS', 'SATS', 'SHIB', 'WHY', 'XEC'}:
                                candidates.append(f"u1000{symbol}USDT")
                        elif exchange_name.lower() == 'coinbase':
                            candidates = [f"{symbol}-USDC", f"{symbol}/USDC"]
                        elif exchange_name.lower() == 'binance':
                            candidates = [f"{symbol}/USDC", f"{symbol}USDC"]
                        elif exchange_name.lower() == 'kucoin':
                            candidates = [f"{symbol}/USDT:USDT", f"{symbol}/USDT", f"{symbol}USDT"]
                        elif exchange_name.lower() in {'bybit', 'okx', 'bitget', 'gateio', 'mexc'}:
                            candidates = [f"{symbol}/USDT:USDT", f"{symbol}/USDT", f"{symbol}USDT"]
                        elif exchange_name.lower() == 'yfinance':
                            candidates = [symbol]
                        else:
                            candidates = [f"{symbol}/USDT", f"{symbol}/USDC", f"{symbol}USDC", f"{symbol}/USDTM", f"{symbol}USDT", f"{symbol}USDTM"]

                        for cand in candidates:
                            try:
                                tmp_df = await loop.run_in_executor(
                                    None,
                                    source.fetch_historical_data,
                                    cand,
                                    timeframe,
                                    min(limit, self.MAX_LIMITS.get(exchange_name.lower(), limit)),
                                    last_timestamp + 1 if last_timestamp else None
                                )
                            except Exception:
                                tmp_df = None
                            if tmp_df is not None and not getattr(tmp_df, 'empty', False):
                                fetch_symbol = cand
                                if hasattr(tmp_df, 'itertuples'):
                                    ohlcv_data = [
                                        [int(getattr(r, 'timestamp').timestamp() * 1000) if hasattr(getattr(r, 'timestamp'), 'timestamp') else int(r[0]), r[1], r[2], r[3], r[4], r[5]]
                                        for r in tmp_df.itertuples(index=False)
                                    ]
                                else:
                                    ohlcv_data = tmp_df
                                break
                    else:
                        # Successful on the canonical pipeline-derived fetch_symbol
                        if hasattr(tmp_df, 'itertuples'):
                            ohlcv_data = [
                                [int(getattr(r, 'timestamp').timestamp() * 1000) if hasattr(getattr(r, 'timestamp'), 'timestamp') else int(r[0]), r[1], r[2], r[3], r[4], r[5]]
                                for r in tmp_df.itertuples(index=False)
                            ]
                        else:
                            ohlcv_data = tmp_df

                else:
                    tmp_df = await loop.run_in_executor(
                        None,
                        source.fetch_historical_data,
                        symbol,
                        timeframe,
                        min(limit, self.MAX_LIMITS.get(exchange_name.lower(), limit)),
                        last_timestamp + 1 if last_timestamp else None
                    )
                    if tmp_df is not None and not getattr(tmp_df, 'empty', False):
                        if hasattr(tmp_df, 'itertuples'):
                            ohlcv_data = [
                                [int(getattr(r, 'timestamp').timestamp() * 1000) if hasattr(getattr(r, 'timestamp'), 'timestamp') else int(r[0]), r[1], r[2], r[3], r[4], r[5]]
                                for r in tmp_df.itertuples(index=False)
                            ]
                        else:
                            ohlcv_data = tmp_df
            except Exception:
                ohlcv_data = None
            
            if ohlcv_data:
                # Store using the original base `symbol` so DB uses base-only symbols
                inserted = self.store_ohlcv_data(exchange_name, symbol, timeframe, ohlcv_data)
                
                # Prune old data to cap disk usage
                if inserted > 0:
                    self.prune_old_data(exchange_name, symbol, timeframe)
                
                return inserted > 0
            return False
                
        except Exception:
            return False  # Silent fail for large batch processing
    
    def discover_all_symbols(self):
        """Auto-discover all symbols from markets_info/."""
        markets_dir = Path(__file__).parent.parent.parent / "markets_info"
        
        if not markets_dir.exists():
            return {}
        
        exchange_symbols = {}
        
        for exchange_dir in markets_dir.iterdir():
            if not exchange_dir.is_dir() or exchange_dir.name == 'symbols_discovery':
                continue
            
            exchange_name = exchange_dir.name
            symbols = set()
            
            # Read all JSON files
            for json_file in exchange_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Pattern 1: Dict with 'universe' field (Hyperliquid)
                        if isinstance(data, dict) and 'universe' in data:
                            if isinstance(data['universe'], list):
                                for item in data['universe']:
                                    if isinstance(item, dict) and 'name' in item:
                                        symbols.add(item['name'])
                        
                        # Pattern 2: Dict with 'symbols' field
                        elif isinstance(data, dict) and 'symbols' in data:
                            if isinstance(data['symbols'], list):
                                for symbol in data['symbols']:
                                    # String format: "BTC/USDT:USDT" (MEXC, Bybit, OKX, Gate.io, Bitget)
                                    if isinstance(symbol, str):
                                        clean_symbol = symbol.split('/')[0]  # Get base currency
                                        symbols.add(clean_symbol)
                                    # Dict format with various fields
                                    elif isinstance(symbol, dict):
                                        # Coinbase uses 'id': "BTC-USDC"
                                        if 'id' in symbol:
                                            raw = symbol['id']
                                            clean_symbol = raw.split('-')[0]
                                            symbols.add(clean_symbol)
                                        # KuCoin uses 'symbol': "BTC/USDT:USDT"
                                        elif 'symbol' in symbol:
                                            raw = symbol['symbol']
                                            if '/' in raw:
                                                clean_symbol = raw.split('/')[0]
                                            elif '-' in raw:
                                                clean_symbol = raw.split('-')[0]
                                            else:
                                                # Remove common quote currencies from end
                                                for quote in ['USDT', 'USDC', 'USD', 'BUSD']:
                                                    if raw.endswith(quote):
                                                        clean_symbol = raw[:-len(quote)]
                                                        break
                                                else:
                                                    clean_symbol = raw
                                            symbols.add(clean_symbol)
                        
                        # Pattern 3: List at root level
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    if 'name' in item:
                                        symbols.add(item['name'])
                                    elif 'symbol' in item:
                                        symbols.add(item['symbol'])
                                elif isinstance(item, str):
                                    symbols.add(item)
                except Exception:
                    continue
            
            if symbols:
                exchange_symbols[exchange_name] = sorted(list(symbols))
        
        return exchange_symbols
    
    def get_statistics(self):
        """Get archive statistics."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT exchange, COUNT(DISTINCT symbol) as symbols, 
                   SUM(total_candles) as total_candles
            FROM fetch_metadata
            GROUP BY exchange
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_disk_usage(self):
        """Get database file size in MB."""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path) / (1024 * 1024)
        return 0
    
    def export_to_csv(self, exchange, symbol, timeframe, output_path):
        """Export archived data to CSV for backtesting."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, open, high, low, close, volume
            FROM ohlcv_data
            WHERE exchange = ? AND symbol = ? AND timeframe = ?
            ORDER BY timestamp
        """, (exchange, symbol, timeframe))
        
        data = cursor.fetchall()
        conn.close()
        
        if data:
            import pandas as pd
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.to_csv(output_path, index=False)
            return len(df)
        return 0


async def run_comprehensive_archive():
    """Archive ALL symbols from ALL exchanges automatically."""
    
    archiver = ComprehensiveArchiver()
    
    print("=" * 80)
    print(f"🗄️  COMPREHENSIVE DAILY ARCHIVE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Load or create config
    config_path = Path(__file__).parent.parent.parent / "archived_data" / "archive_config.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {
            "timeframes_to_archive": ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"],
            "fetch_limit": 1500,
            "progress_update_every": 50,
            "retention_note": "See RETENTION_POLICIES in code for disk space management",
            "rate_limiting_note": "Token bucket rate limiting enabled per exchange (Hyperliquid: 10 req/s, others: 5 req/s)"
        }
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Created config: {config_path}\n")
    
    # Auto-discover ALL symbols
    print("🔍 Auto-discovering symbols from markets_info/...")
    all_exchange_symbols = archiver.discover_all_symbols()
    
    # Load main config.json to check which exchanges are enabled
    main_config_path = Path(__file__).parent.parent.parent / "config.json"
    enabled_exchanges = set()
    if main_config_path.exists():
        try:
            with open(main_config_path, 'r', encoding='utf-8-sig') as f:
                main_config = json.load(f)
                for exchange in all_exchange_symbols.keys():
                    use_flag = f"use_{exchange}"
                    if main_config.get(use_flag, False):
                        enabled_exchanges.add(exchange)
        except Exception as e:
            print(f"⚠️  Warning: Could not read {main_config_path}: {e}")
            print(f"⚠️  Enabling all exchanges with symbols")
            enabled_exchanges = set(all_exchange_symbols.keys())
    else:
        # If no config.json, enable all exchanges that have symbols
        enabled_exchanges = set(all_exchange_symbols.keys())
    
    # Filter to only enabled exchanges
    all_exchange_symbols = {ex: syms for ex, syms in all_exchange_symbols.items() if ex in enabled_exchanges}
    
    # CRITICAL: Sort exchanges by PRIORITY ORDER (Hyperliquid MUST be first!)
    exchange_symbols = {}
    for exchange in archiver.EXCHANGE_PRIORITY:
        if exchange in all_exchange_symbols:
            exchange_symbols[exchange] = all_exchange_symbols[exchange]
    
    # Add any remaining exchanges not in priority list
    for exchange, symbols in all_exchange_symbols.items():
        if exchange not in exchange_symbols:
            exchange_symbols[exchange] = symbols
    
    total_symbols = sum(len(symbols) for symbols in exchange_symbols.values())
    print(f"✅ Found {total_symbols} symbols across {len(exchange_symbols)} exchanges\n")
    
    print("📋 Exchange order (HYPERLIQUID FIRST for maximum data):")
    for i, (exchange, symbols) in enumerate(exchange_symbols.items(), 1):
        max_limit = archiver.MAX_LIMITS.get(exchange, 1500)
        print(f"   {i}. {exchange:15} ({len(symbols):4} symbols) → max {max_limit:,} candles/fetch")
    print()
    
    # Calculate total tasks
    timeframes = config['timeframes_to_archive']
    total_tasks = total_symbols * len(timeframes)
    
    print(f"\n📊 Archiving {total_tasks} combinations")
    print(f"   ({total_symbols} symbols × {len(timeframes)} timeframes: {', '.join(timeframes)})")
    print(f"💾 Retention policies active (prevents disk bloat)\n")
    
    # Archive everything IN PRIORITY ORDER (Hyperliquid first for best data)
    completed = 0
    successful = 0
    start_time = datetime.now()
    
    # Sort exchanges by priority (Hyperliquid first)
    prioritized_exchanges = []
    for exchange in archiver.EXCHANGE_PRIORITY:
        if exchange in exchange_symbols:
            prioritized_exchanges.append((exchange, exchange_symbols[exchange]))
    
    # Add any remaining exchanges not in priority list
    for exchange, symbols in exchange_symbols.items():
        if exchange not in archiver.EXCHANGE_PRIORITY:
            prioritized_exchanges.append((exchange, symbols))
    
    print(f"📋 Archive order (prioritized by data quality):")
    for i, (exchange, symbols) in enumerate(prioritized_exchanges, 1):
        max_limit = archiver.MAX_LIMITS.get(exchange, 1000)
        print(f"   {i}. {exchange:15} ({len(symbols):4} symbols) → max {max_limit:,} candles/fetch")
    print()
    
    for exchange, symbols in prioritized_exchanges:
        print(f"\n📡 {exchange} ({len(symbols)} symbols)...")
        
        for i, symbol in enumerate(symbols, 1):
            for timeframe in timeframes:
                success = await archiver.archive_symbol(
                    exchange, symbol, timeframe,
                    limit=config['fetch_limit']
                )
                
                completed += 1
                if success:
                    successful += 1
                
            
            # Progress updates
            if i % config['progress_update_every'] == 0:
                progress = (completed / total_tasks) * 100
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                print(f"   {i}/{len(symbols)} symbols ({progress:.1f}% overall, {elapsed:.1f}min elapsed)")
        
        print(f"   ✅ Completed {exchange}")
    
    # Final statistics
    print("\n" + "=" * 80)
    print("📊 ARCHIVE STATISTICS")
    print("=" * 80)
    
    stats = archiver.get_statistics()
    total_candles = 0
    
    for exchange, symbol_count, candles in stats:
        print(f"{exchange:15} {symbol_count:5} symbols → {candles:>12,} candles")
        total_candles += candles
    
    disk_usage = archiver.get_disk_usage()
    elapsed_total = (datetime.now() - start_time).total_seconds() / 60
    
    print(f"\n💾 Database: {disk_usage:.2f} MB")
    print(f"📊 Total candles: {total_candles:,}")
    print(f"✅ Success rate: {successful}/{completed} ({successful/completed*100:.1f}%)")
    print(f"⏱️  Total time: {elapsed_total:.1f} minutes")
    print(f"\n🎯 Archive complete - prepared for ANY client request!")
    print(f"📈 Dataset grows daily: 5k → 50k+ candles over 6-12 months")
    
    # Proper exit for scheduled tasks
    print("\n⏹️  Exiting...")
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_comprehensive_archive())
        sys.exit(exit_code if exit_code else 0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Archive interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
