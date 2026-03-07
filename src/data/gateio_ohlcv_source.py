"""
Gate.io OHLCV Data Source
Provides clean interface for fetching Gate.io OHLCV data using CCXT
"""

import logging
import pandas as pd
import ccxt
import time
from datetime import datetime, timedelta
from typing import Optional
import json
from src.exchange.config import load_config
import os

logger = logging.getLogger(__name__)


class GateioOHLCVDataSource:
    """Fetches OHLCV data from Gate.io using CCXT - uses SWAP (perpetuals)"""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 market_type: str = 'swap'):
        """Initialize Gate.io CCXT client for swap (perpetuals)."""
        self.api_key = api_key or os.environ.get('GATEIO_API_KEY')
        self.api_secret = api_secret or os.environ.get('GATEIO_API_SECRET')
        if not self.api_key or not self.api_secret:
            try:
                config = load_config()
                self.api_key = self.api_key or config.get('gateio_api_key')
                self.api_secret = self.api_secret or config.get('gateio_api_secret')
            except Exception as e:
                logger.warning(f'Could not load Gate.io API credentials: {e}')

        # Treat placeholder strings as None for public API access
        if self.api_key and ('YOUR_' in self.api_key.upper() or self.api_key == ''):
            self.api_key = None
        if self.api_secret and ('YOUR_' in self.api_secret.upper() or self.api_secret == ''):
            self.api_secret = None

        self.market_type = market_type
        config = {
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': market_type,
            },
        }
        self.exchange = ccxt.gateio(config)  # type: ignore
        logger.info(f"Initialized GateioOHLCVDataSource for {market_type}")

    def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 1000,
        since: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Gate.io.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT' or 'BTC/USDT:USDT')
            timeframe: Timeframe ('1m', '5m', '15m', '1h', '4h', etc.)
            limit: Number of candles to fetch (max 1000 for Gate.io)
            since: Timestamp in milliseconds (optional)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Normalise symbol to perpetuals format
            if '/' not in symbol:
                symbol = f"{symbol}/USDT:USDT"
            elif self.market_type == 'swap' and ':USDT' not in symbol:
                symbol = f"{symbol}:USDT"

            logger.debug(f"Fetching Gate.io data for {symbol} ({timeframe}), limit={limit}")

            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=min(limit, 1000),
                since=since
            )

            if not ohlcv:
                logger.warning(f"No OHLCV data returned for {symbol} ({timeframe})")
                return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna()

            logger.info(f"Successfully fetched {len(df)} candles for {symbol} ({timeframe})")
            return df

        except Exception as e:
            logger.error(f"Error fetching Gate.io data for {symbol} ({timeframe}): {e}")
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    def get_available_timeframes(self) -> list:
        """Get list of supported timeframes for Gate.io SWAP."""
        return ['10s', '1m', '5m', '15m', '30m', '1h', '2h', '4h', '8h', '1d', '7d']
