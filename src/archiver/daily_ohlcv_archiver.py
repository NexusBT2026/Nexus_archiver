"""
Daily OHLCV Archiver - Accumulates historical data over time for superior backtesting.

This module fetches and stores OHLCV data incrementally, building a proprietary dataset
that grows beyond standard API limits (5000 → 50,000+ candles over 6-12 months).

Run this script daily via Windows Task Scheduler to continuously accumulate data.
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


class OHLCVArchiver:
    """Incrementally archive OHLCV data to build long-term datasets."""
    
    def __init__(self, db_path="archived_data/nexus_archive.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
        
        # Map of exchange names to their source classes
        self.exchange_sources = {
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
            'yfinance': YFinanceOHLCVDataSource,
        }
    
    def _ensure_db_directory(self):
        """Create archived_data directory if it doesn't exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database with optimized schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main OHLCV table with composite primary key
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
        
        # Metadata table to track last fetch per symbol
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
        
        # Index for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_time 
            ON ohlcv_data(symbol, timeframe, timestamp)
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized: {self.db_path}")
    
    def get_last_timestamp(self, exchange, symbol, timeframe):
        """Get the last stored timestamp for incremental fetching."""
        conn = sqlite3.connect(self.db_path)
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
        if not ohlcv_data or len(ohlcv_data) == 0:
            return 0
        
        conn = sqlite3.connect(self.db_path)
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
                    candle[0],  # timestamp
                    candle[1],  # open
                    candle[2],  # high
                    candle[3],  # low
                    candle[4],  # close
                    candle[5],  # volume
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.IntegrityError:
                continue  # Duplicate, skip
        
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
    
    async def archive_symbol(self, exchange_name, symbol, timeframe, limit=1000):
        """Archive a single symbol's data incrementally."""
        print(f"\n📊 Archiving {exchange_name} {symbol} {timeframe}...")
        
        # Get exchange source
        source_class = self.exchange_sources.get(exchange_name.lower())
        if not source_class:
            print(f"❌ Unknown exchange: {exchange_name}")
            return
        
        source = source_class()
        
        # Get last timestamp for incremental fetch
        last_timestamp = self.get_last_timestamp(exchange_name, symbol, timeframe)
        
        if last_timestamp:
            # Fetch since last timestamp
            since_ms = last_timestamp + 1  # Start after last candle
            print(f"   Fetching since {datetime.fromtimestamp(since_ms/1000)}")
        else:
            # First fetch - get maximum available
            since_ms = None
            print(f"   First fetch - getting max available candles")
        
        try:
            loop = asyncio.get_event_loop()

            if exchange_name.lower() == 'hyperliquid':
                # Hyperliquid uses lookback_days, not since/limit
                lookback = 30 if since_ms else 730
                df = await loop.run_in_executor(
                    None, source.fetch_historical_data, symbol, timeframe, lookback
                )
            else:
                df = await loop.run_in_executor(
                    None, source.fetch_historical_data, symbol, timeframe, limit, since_ms
                )

            # Convert DataFrame → list of [timestamp_ms, o, h, l, c, v]
            ohlcv_data = []
            if df is not None and not df.empty:
                for row in df.itertuples(index=False):
                    ts = row.timestamp
                    ts_ms = int(ts.timestamp() * 1000) if hasattr(ts, 'timestamp') else int(ts)
                    ohlcv_data.append([ts_ms, row.open, row.high, row.low, row.close, row.volume])

            if ohlcv_data:
                inserted = self.store_ohlcv_data(exchange_name, symbol, timeframe, ohlcv_data)
                print(f"   ✅ Stored {inserted} new candles (fetched {len(ohlcv_data)} total)")
            else:
                print(f"   ⚠️ No data returned")

        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def get_statistics(self):
        """Get archive statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT exchange, symbol, timeframe, total_candles, last_fetch_date
            FROM fetch_metadata
            ORDER BY exchange, symbol, timeframe
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def export_to_csv(self, exchange, symbol, timeframe, output_path):
        """Export archived data to CSV for backtesting."""
        conn = sqlite3.connect(self.db_path)
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
            print(f"✅ Exported {len(df)} candles to {output_path}")
        else:
            print(f"❌ No data found for {exchange} {symbol} {timeframe}")


async def archive_daily_run():
    """Daily archive run - fetch latest data for configured symbols."""
    
    # Load configuration
    config_path = Path(__file__).parent.parent.parent / "archived_data" / "archive_config.json"
    
    if not config_path.exists():
        print(f"⚠️ Archive config not found: {config_path}")
        print("Creating default configuration...")
        
        default_config = {
            "symbols_to_archive": [
                {"exchange": "binance", "symbol": "BTC/USDT:USDT", "timeframes": ["1h", "4h", "1d"]},
                {"exchange": "binance", "symbol": "ETH/USDT:USDT", "timeframes": ["1h", "4h", "1d"]},
                {"exchange": "bybit", "symbol": "BTC/USDT:USDT", "timeframes": ["1h", "4h", "1d"]},
            ],
            "fetch_limit": 1000,
            "delay_between_requests": 1.0
        }
        
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"✅ Created default config: {config_path}")
        print("Edit this file to add more symbols to archive.")
        return
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    archiver = OHLCVArchiver()
    
    print("=" * 60)
    print(f"🗄️  OHLCV DAILY ARCHIVE RUN - {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Archive each configured symbol
    for item in config['symbols_to_archive']:
        exchange = item['exchange']
        symbol = item['symbol']
        timeframes = item['timeframes']
        
        for timeframe in timeframes:
            await archiver.archive_symbol(
                exchange, 
                symbol, 
                timeframe, 
                limit=config.get('fetch_limit', 1000)
            )
            await asyncio.sleep(config.get('delay_between_requests', 1.0))
    
    # Show statistics
    print("\n" + "=" * 60)
    print("📊 ARCHIVE STATISTICS")
    print("=" * 60)
    
    stats = archiver.get_statistics()
    for exchange, symbol, timeframe, total_candles, last_fetch in stats:
        print(f"{exchange:10} {symbol:20} {timeframe:5} → {total_candles:6} candles (last: {last_fetch[:10]})")
    
    print("\n✅ Daily archive run complete!")


if __name__ == "__main__":
    asyncio.run(archive_daily_run())
