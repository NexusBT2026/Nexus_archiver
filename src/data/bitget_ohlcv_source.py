"""
Bitget OHLCV Data Source
Provides clean interface for fetching Bitget OHLCV data using CCXT
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


class BitgetOHLCVDataSource:
    """Fetches OHLCV data from Bitget using CCXT - uses SWAP (perpetuals)"""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 passphrase: Optional[str] = None, market_type: str = 'swap'):
        """Initialize Bitget CCXT client for swap (perpetuals)."""
        self.api_key = api_key or os.environ.get('BITGET_API_KEY')
        self.api_secret = api_secret or os.environ.get('BITGET_API_SECRET')
        self.passphrase = passphrase or os.environ.get('BITGET_PASSPHRASE')
        if not self.api_key or not self.api_secret:
            try:
                config = load_config()
                self.api_key = self.api_key or config.get('bitget_api_key')
                self.api_secret = self.api_secret or config.get('bitget_api_secret')
                self.passphrase = self.passphrase or config.get('bitget_passphrase')
            except Exception as e:
                logger.warning(f'Could not load Bitget API credentials: {e}')

        # Treat placeholder strings as None for public API access
        if self.api_key and ('YOUR_' in self.api_key.upper() or self.api_key == ''):
            self.api_key = None
        if self.api_secret and ('YOUR_' in self.api_secret.upper() or self.api_secret == ''):
            self.api_secret = None

        self.market_type = market_type
        config = {
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': market_type,
            },
        }
        self.exchange = ccxt.bitget(config)  # type: ignore
        logger.info(f"Initialized BitgetOHLCVDataSource for {market_type}")

    def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 1000,
        since: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Bitget.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT' or 'BTC/USDT:USDT')
            timeframe: Timeframe ('1m', '5m', '15m', '1h', '4h', etc.)
            limit: Number of candles to fetch (max 1000 for Bitget)
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

            logger.debug(f"Fetching Bitget data for {symbol} ({timeframe}), limit={limit}")

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
            logger.error(f"Error fetching Bitget data for {symbol} ({timeframe}): {e}")
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    def get_available_timeframes(self) -> list:
        """Get list of supported timeframes for Bitget SWAP."""
        return ['1m', '5m', '15m', '30m', '1h', '4h', '6h', '12h', '1d', '3d', '1w', '1M']
