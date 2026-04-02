# Future Exchange & Data Source Expansion

## Overview
Nexus Archiver currently supports **11 exchanges** covering major CEX crypto and stocks. This document outlines **50+ additional sources** to maximize trader reach across all markets: DEX, DeFi, regional CEX, derivatives, options, prediction markets, and alternative assets.

---

## Current Coverage (11 Exchanges)
✅ **Centralized Crypto**: Binance, Bybit, OKX, MEXC, Phemex, KuCoin, Bitget, Gate.io, Coinbase  
✅ **Stocks/ETFs**: YFinance  
✅ **DEX Perpetuals**: Hyperliquid  

**Total Symbols**: ~3,400  
**Daily Volume Covered**: ~$80B (estimated)

---

## Priority 1: Major DEX Perpetuals (Add Next)

### 1. **dYdX V4** ⭐⭐⭐⭐⭐
- **Type**: Decentralized perpetuals (Cosmos-based)
- **Volume**: $500M-$1B daily
- **API**: `https://indexer.dydx.trade/v4/candles` (direct OHLCV)
- **Symbols**: ~50 perpetual markets
- **Why**: 2nd largest decentralized perps after Hyperliquid
- **Implementation**: EASY (similar to Hyperliquid)

### 2. **Vertex Protocol** ⭐⭐⭐⭐
- **Type**: Decentralized perpetuals (Arbitrum)
- **Volume**: $50M-$150M daily
- **API**: REST API with OHLCV endpoints
- **Symbols**: ~30 perpetuals
- **Why**: Fast-growing orderbook DEX
- **Implementation**: EASY

### 3. **GMX V2** ⭐⭐⭐
- **Type**: Decentralized perpetuals (Arbitrum/Avalanche)
- **Volume**: $100M-$200M daily
- **API**: The Graph or direct contracts
- **Symbols**: ~15 perpetuals
- **Why**: Popular with retail traders
- **Implementation**: MODERATE (oracle-based pricing)

### 4. **Apex Protocol** ⭐⭐⭐
- **Type**: Cross-chain perpetuals
- **Volume**: $20M-$50M daily
- **API**: REST API available
- **Symbols**: ~40 perpetuals
- **Implementation**: EASY

---

## Priority 2: Major Spot DEX (High Volume)

### 5. **Uniswap V3** ⭐⭐⭐⭐⭐
- **Type**: Spot AMM DEX
- **Volume**: $1B-$2B daily (LARGEST DEX)
- **Chains**: Ethereum, Polygon, Arbitrum, Optimism, Base
- **API**: The Graph subgraphs
- **Symbols**: 1000+ pools
- **Implementation**: MODERATE (construct OHLCV from swap events)

### 6. **PancakeSwap V3** ⭐⭐⭐⭐
- **Type**: Spot AMM DEX
- **Volume**: $400M-$600M daily
- **Chains**: BSC, Ethereum, Polygon zkEVM, Arbitrum
- **API**: The Graph + BSC RPC
- **Symbols**: 800+ pools
- **Implementation**: MODERATE

### 7. **Raydium** ⭐⭐⭐⭐
- **Type**: Spot AMM + CLMM (Solana)
- **Volume**: $200M-$500M daily
- **API**: Raydium API + Solana RPC
- **Symbols**: 500+ pools
- **Implementation**: MODERATE (Solana program logs)

### 8. **Curve Finance** ⭐⭐⭐
- **Type**: Stablecoin-focused DEX
- **Volume**: $100M-$300M daily
- **Chains**: Ethereum, Polygon, Arbitrum, Optimism, Fantom
- **API**: The Graph
- **Symbols**: 200+ pools
- **Why**: Best stablecoin liquidity
- **Implementation**: MODERATE

### 9. **Jupiter Aggregator** ⭐⭐⭐⭐
- **Type**: DEX Aggregator (Solana)
- **Volume**: Aggregates all Solana DEXs
- **API**: `https://quote-api.jup.ag/v6/`
- **Symbols**: 1000+ tokens
- **Why**: Best price discovery on Solana
- **Implementation**: EASY

### 10. **1inch Aggregator** ⭐⭐⭐
- **Type**: DEX Aggregator (Multi-chain)
- **Volume**: Aggregates 200+ DEXs
- **API**: REST API
- **Chains**: Ethereum, BSC, Polygon, Arbitrum, Optimism
- **Implementation**: EASY

---

## Priority 3: Regional CEX (Emerging Markets)

### 11. **Kraken** ⭐⭐⭐⭐
- **Region**: Global (strong in Europe)
- **Volume**: $1B-$2B daily
- **API**: REST + WebSocket
- **Why**: Major regulated exchange, missing from current list

### 12. **Crypto.com** ⭐⭐⭐
- **Region**: Asia/Global
- **Volume**: $500M-$1B daily
- **API**: REST API
- **Why**: Large retail user base

### 13. **Huobi (HTX)** ⭐⭐⭐
- **Region**: Asia
- **Volume**: $500M-$1B daily
- **API**: REST API
- **Why**: Strong presence in Asia

### 14. **Bitfinex** ⭐⭐⭐
- **Region**: Global
- **Volume**: $200M-$500M daily
- **API**: REST API
- **Why**: Popular with institutional traders

### 15. **Bitstamp** ⭐⭐
- **Region**: Europe/US
- **Volume**: $100M-$200M daily
- **API**: REST API
- **Why**: Oldest exchange, institutional access

### 16. **Upbit** ⭐⭐⭐
- **Region**: South Korea
- **Volume**: $1B-$2B daily
- **API**: REST API (KRW pairs)
- **Why**: Largest Korean exchange

### 17. **Bithumb** ⭐⭐
- **Region**: South Korea
- **Volume**: $300M-$500M daily
- **API**: REST API

### 18. **Coincheck** ⭐⭐
- **Region**: Japan
- **Volume**: $100M-$200M daily
- **API**: REST API
- **Why**: Major Japanese exchange

### 19. **bitFlyer** ⭐⭐
- **Region**: Japan
- **Volume**: $50M-$100M daily
- **API**: REST API

### 20. **WazirX** ⭐⭐
- **Region**: India
- **Volume**: $50M-$100M daily
- **API**: REST API (Binance-owned)

### 21. **CoinDCX** ⭐⭐
- **Region**: India
- **Volume**: $20M-$50M daily
- **API**: REST API

### 22. **Mercado Bitcoin** ⭐
- **Region**: Latin America (Brazil)
- **Volume**: $10M-$30M daily
- **API**: REST API

---

## Priority 4: Options & Derivatives

### 23. **Deribit** ⭐⭐⭐⭐⭐
- **Type**: Crypto options & futures
- **Volume**: $1B-$2B daily (LARGEST crypto options)
- **API**: REST + WebSocket
- **Products**: BTC/ETH options, perpetuals
- **Why**: 90%+ market share in crypto options
- **Implementation**: EASY

### 24. **Lyra Finance** ⭐⭐⭐
- **Type**: Decentralized options (Ethereum)
- **API**: The Graph + REST API
- **Products**: Options chains, IV surfaces
- **Implementation**: MODERATE

### 25. **Aevo (Ribbon)** ⭐⭐⭐
- **Type**: Options + perpetuals DEX
- **API**: REST API
- **Products**: Options, perpetuals
- **Implementation**: EASY

### 26. **Paradigm** ⭐⭐
- **Type**: Institutional derivatives
- **API**: Requires institutional access
- **Products**: Options, structured products

### 27. **Delta Exchange** ⭐⭐
- **Type**: Crypto derivatives
- **Volume**: $50M-$100M daily
- **API**: REST API
- **Products**: Perpetuals, futures, options

---

## Priority 5: Prediction Markets

### 28. **Polymarket** ⭐⭐⭐⭐
- **Type**: Decentralized prediction market (Polygon)
- **Volume**: $1B+ total (spikes during events)
- **API**: CLOB API
- **Markets**: Politics, sports, crypto, macro
- **Why**: Largest prediction market, unique data
- **Implementation**: MODERATE

### 29. **Augur** ⭐⭐
- **Type**: Decentralized prediction market (Ethereum)
- **API**: The Graph
- **Implementation**: MODERATE

### 30. **Azuro** ⭐⭐
- **Type**: Sports betting protocol
- **API**: The Graph
- **Implementation**: MODERATE

---

## Priority 6: Additional Spot DEX

### 31. **Orca** ⭐⭐⭐
- **Type**: Spot DEX (Solana)
- **Volume**: $50M-$150M daily
- **API**: Orca API + Solana RPC
- **Implementation**: MODERATE

### 32. **SushiSwap** ⭐⭐⭐
- **Type**: Spot AMM (Multi-chain)
- **Volume**: $100M-$200M daily
- **API**: The Graph
- **Chains**: Ethereum, Polygon, Arbitrum, etc.
- **Implementation**: MODERATE

### 33. **Balancer** ⭐⭐
- **Type**: Weighted pool AMM
- **Volume**: $50M-$100M daily
- **API**: The Graph
- **Implementation**: MODERATE

### 34. **TraderJoe** ⭐⭐
- **Type**: Spot DEX (Avalanche)
- **Volume**: $30M-$80M daily
- **API**: The Graph
- **Implementation**: MODERATE

### 35. **Osmosis** ⭐⭐⭐
- **Type**: Spot DEX (Cosmos)
- **Volume**: $20M-$50M daily
- **API**: Cosmos RPC + Osmosis API
- **Implementation**: MODERATE

---

## Priority 7: Exotic/Alternative Markets

### 36. **Synthetix** ⭐⭐⭐
- **Type**: Synthetic assets (Ethereum/Optimism)
- **API**: The Graph
- **Products**: Synths (sUSD, sBTC, etc.)
- **Why**: Unique synthetic exposure
- **Implementation**: MODERATE

### 37. **dYdX V3** ⭐⭐
- **Type**: Legacy perpetuals (Ethereum L2)
- **Note**: Being phased out for V4, but historical data valuable
- **API**: REST API
- **Implementation**: EASY

### 38. **BTSE** ⭐⭐
- **Type**: CEX with spot + futures
- **Volume**: $50M-$100M daily
- **API**: REST API
- **Implementation**: EASY

### 39. **CoinEx** ⭐⭐
- **Type**: CEX (China-friendly)
- **Volume**: $100M-$200M daily
- **API**: REST API
- **Implementation**: EASY

### 40. **BingX** ⭐⭐
- **Type**: CEX with copy trading
- **Volume**: $1B-$2B daily
- **API**: REST API
- **Implementation**: EASY

---

## Priority 8: Forex & Traditional Markets

### 41. **OANDA** ⭐⭐⭐⭐
- **Type**: Forex broker
- **Products**: 70+ currency pairs
- **API**: REST API (requires account)
- **Why**: Real forex data (not crypto/USDT pairs)
- **Implementation**: EASY

### 42. **Interactive Brokers** ⭐⭐⭐⭐⭐
- **Type**: Multi-asset broker
- **Products**: Stocks, options, futures, forex, bonds
- **API**: TWS API (requires account)
- **Why**: Access to ALL traditional markets
- **Implementation**: MODERATE (proprietary API)

### 43. **Alpaca** ⭐⭐⭐⭐
- **Type**: Stock broker API
- **Products**: US stocks, options (paper trading free)
- **API**: REST API (free tier available)
- **Why**: Real-time US stock data
- **Implementation**: EASY

### 44. **Polygon.io** ⭐⭐⭐⭐
- **Type**: Stock/Crypto data provider
- **API**: REST API ($199/mo for crypto+stocks)
- **Products**: Real-time + historical for stocks/crypto
- **Why**: Professional-grade data quality
- **Implementation**: EASY

### 45. **Alpha Vantage** ⭐⭐⭐
- **Type**: Stock/Forex/Crypto data provider
- **API**: REST API (free tier: 25 calls/day)
- **Products**: Stocks, forex, crypto, indicators
- **Implementation**: EASY

---

## Priority 9: Commodities & Futures

### 46. **CME Group Data** ⭐⭐⭐⭐
- **Type**: Futures exchange data
- **Products**: Bitcoin futures, ES, NQ, CL, GC
- **API**: Requires data subscription
- **Why**: Institutional-grade futures data

### 47. **TradingView** ⭐⭐⭐⭐
- **Type**: Multi-asset charting platform
- **API**: Unofficial scraping or paid partnership
- **Products**: Stocks, crypto, forex, commodities
- **Why**: Unified access to multiple data sources

---

## Priority 10: Niche DEX & DeFi Protocols

### 48. **Maverick Protocol** ⭐⭐
- **Type**: Dynamic AMM (Multi-chain)
- **API**: The Graph
- **Implementation**: MODERATE

### 49. **Drift Protocol** ⭐⭐⭐
- **Type**: Perpetuals DEX (Solana)
- **Volume**: $20M-$50M daily
- **API**: REST API
- **Implementation**: EASY

### 50. **Rainbow Protocol** ⭐⭐
- **Type**: Cross-chain bridge aggregator
- **Data**: Cross-chain flow, arbitrage opportunities
- **Implementation**: MODERATE

### 51. **Pendle Finance** ⭐⭐
- **Type**: Yield trading protocol
- **API**: The Graph
- **Products**: Tokenized yield positions
- **Implementation**: MODERATE

### 52. **Perpetual Protocol** ⭐⭐
- **Type**: Virtual AMM perpetuals (Optimism)
- **Volume**: $10M-$30M daily
- **API**: The Graph
- **Implementation**: MODERATE

### 53. **Level Finance** ⭐⭐
- **Type**: Perpetuals DEX (BSC)
- **API**: REST API
- **Implementation**: EASY

### 54. **MUX Protocol** ⭐⭐
- **Type**: Perpetuals aggregator
- **API**: REST API
- **Implementation**: EASY

---

## Priority 11: Aggregated Data Providers

### 55. **CoinGecko API** ⭐⭐⭐⭐
- **Coverage**: 200+ DEXs, 800+ CEXs aggregated
- **API**: Free tier (10-50 calls/min)
- **Products**: Aggregate prices, volume, market cap
- **Why**: Quick way to add hundreds of exchanges
- **Limitation**: No 1-minute candles (hourly/daily only)

### 56. **CoinMarketCap API** ⭐⭐⭐⭐
- **Coverage**: Similar to CoinGecko
- **API**: Free tier (10K credits/mo)
- **Limitation**: Similar restrictions

### 57. **The Graph (Protocol)** ⭐⭐⭐⭐⭐
- **Coverage**: 40+ blockchains, 1000+ subgraphs
- **API**: GraphQL (free tier 1K queries/day)
- **Why**: **Recommended** for indexing most DEX data
- **Cost**: Free tier or $100+/mo for higher limits

### 58. **Dune Analytics API** ⭐⭐⭐⭐
- **Coverage**: All major chains
- **API**: SQL queries over blockchain data
- **Cost**: $399/mo minimum
- **Why**: Pre-built DEX/DeFi dashboards available

### 59. **Flipside Crypto** ⭐⭐⭐
- **Coverage**: 20+ blockchains
- **API**: SQL queries (free tier 10K queries/mo)
- **Why**: Good for historical analysis

---

## Implementation Roadmap

### **Phase 1: Perpetuals Expansion** (Weeks 1-2)
Add 4 perpetual DEXs to maximize derivatives coverage:
1. dYdX V4
2. Vertex Protocol  
3. GMX V2
4. Drift Protocol

**Result**: 5 perpetual DEX sources (Hyperliquid + 4 new)

### **Phase 2: Spot DEX Expansion** (Weeks 3-4)
Add 3 major spot DEXs:
1. Jupiter Aggregator (Solana - easiest)
2. Uniswap V3 (Ethereum - largest)
3. PancakeSwap V3 (BSC - 2nd largest)

**Result**: 3 spot DEX sources covering top 3 chains

### **Phase 3: Regional CEX** (Weeks 5-6)
Add 4 regional exchanges:
1. Kraken (Europe/US)
2. Upbit (Korea)
3. Crypto.com (Asia)
4. Huobi/HTX (Asia)

**Result**: 13 CEX sources (current 9 + 4 new)

### **Phase 4: Options & Derivatives** (Weeks 7-8)
Add options trading:
1. Deribit (crypto options leader)
2. Lyra Finance (decentralized options)
3. Aevo (options DEX)

**Result**: Options data for BTC/ETH

### **Phase 5: Prediction Markets** (Week 9)
Add prediction markets:
1. Polymarket (largest)
2. Augur (decentralized)

**Result**: Alternative data sources for sentiment

### **Phase 6: Traditional Markets** (Weeks 10-12)
Expand traditional coverage:
1. Alpaca (US stocks API)
2. Polygon.io (pro stock data)
3. OANDA (real forex data)

**Result**: Professional-grade traditional market data

---

## Technical Implementation Strategy

### For DEX Sources (Need OHLCV Construction)
```python
class UniswapOHLCVDataSource(OHLCVDataSource):
    async def fetch_ohlcv(self, symbol, timeframe, since=None, limit=1000):
        # Query swap events from The Graph
        swaps = await self._query_swaps(pool_address, since, limit)
        
        # Group by timeframe and construct candles
        candles = []
        for period in group_by_timeframe(swaps, timeframe):
            candle = {
                'timestamp': period.start_time,
                'open': period.swaps[0].price,
                'high': max(s.price for s in period.swaps),
                'low': min(s.price for s in period.swaps),
                'close': period.swaps[-1].price,
                'volume': sum(s.volume for s in period.swaps)
            }
            candles.append(candle)
        
        return candles
```

### For CEX Sources (Direct OHLCV)
```python
class KrakenOHLCVDataSource(OHLCVDataSource):
    async def fetch_ohlcv(self, symbol, timeframe, since=None, limit=1000):
        # Direct OHLCV endpoint
        url = f"{self.base_url}/OHLC"
        params = {
            'pair': self._format_symbol(symbol),
            'interval': self._map_timeframe(timeframe),
            'since': since
        }
        response = await self._make_request(url, params)
        return self._parse_candles(response)
```

### Using The Graph (GraphQL)
```python
async def query_uniswap_swaps(pool_address, from_time, to_time):
    query = """
    {
      swaps(
        where: {
          pool: "%s"
          timestamp_gte: %d
          timestamp_lte: %d
        }
        orderBy: timestamp
        first: 1000
      ) {
        timestamp
        amount0
        amount1
        sqrtPriceX96
      }
    }
    """ % (pool_address, from_time, to_time)
    
    response = await post(GRAPH_API_URL, json={'query': query})
    return response['data']['swaps']
```

---

## Database Schema (No Changes Needed)

Current schema supports ALL sources:
```sql
CREATE TABLE ohlcv_data (
    exchange TEXT,      -- Use: 'dydx', 'uniswap_v3_ethereum', 'kraken', etc.
    symbol TEXT,        -- Native format per exchange
    timeframe TEXT,     -- Standard 15 timeframes
    timestamp INTEGER,  -- Unix timestamp (ms)
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    PRIMARY KEY (exchange, symbol, timeframe, timestamp)
)
```

**Naming Convention**:
- CEX: Lowercase exchange name (`kraken`, `deribit`, `upbit`)
- DEX Spot: `{protocol}_v{version}_{chain}` (e.g., `uniswap_v3_ethereum`)
- DEX Perps: Protocol name (`dydx`, `gmx`, `vertex`)
- Aggregators: `{name}_agg` (e.g., `jupiter_agg`, `1inch_agg`)

---

## Cost Considerations

### Free Tier Sources
- **DEX via The Graph**: 1,000 queries/day free
- **Alpaca**: Paper trading free (delayed data)
- **Alpha Vantage**: 25 calls/day free
- **Flipside Crypto**: 10K queries/month free
- **CoinGecko**: 10-50 calls/min free

### Paid Sources (Worth It)
- **The Graph**: $100+/mo for production limits
- **Polygon.io**: $199+/mo for crypto+stocks real-time
- **Dune Analytics**: $399/mo for API access
- **Deribit**: Free API, professional market data

### Institutional (High Cost)
- **Interactive Brokers**: Requires trading account ($10K+ minimum)
- **CME Data**: Expensive subscription ($500-$5000/mo)
- **Bloomberg Terminal**: $2,000/mo (overkill for most traders)

---

## Parallel Execution Strategy

With 50+ sources, reorganize into **5 parallel archivers**:

### Archiver 1: CEX Crypto (Current + 4 new regional)
- Binance, Bybit, OKX, MEXC, Phemex, KuCoin, Bitget, Gate.io, Coinbase
- **Add**: Kraken, Crypto.com, Huobi, Upbit
- **Total**: 13 CEX exchanges

### Archiver 2: Stocks & Traditional
- YFinance (current)
- **Add**: Alpaca, Polygon.io, OANDA (forex)
- **Total**: 4 traditional sources

### Archiver 3: DEX Perpetuals
- Hyperliquid (current)
- **Add**: dYdX V4, Vertex, GMX, Drift
- **Total**: 5 DEX perpetual sources

### Archiver 4: DEX Spot
- **Add**: Jupiter, Uniswap V3, PancakeSwap V3, Raydium
- **Total**: 4 spot DEX sources

### Archiver 5: Derivatives & Alternatives
- **Add**: Deribit (options), Lyra, Polymarket (prediction markets)
- **Total**: 3+ specialized sources

**Expected Runtime**: ~8 hours per archiver (40 hours total if sequential, 8 hours if 5 parallel)

---

## Data Volume Projections

### Current State
- **11 exchanges**: ~3,400 symbols
- **Database size**: ~30GB (184M candles)
- **Daily API calls**: ~51,000

### After Full Expansion (50+ sources)
- **50+ exchanges**: ~15,000 symbols (estimated)
- **Database size**: ~150GB (projected)
- **Daily API calls**: ~225,000
- **Parallel execution**: Still ~8 hours with 5 archivers

---

## Rate Limiting & API Keys

### Current Sources (No API Keys)
All current 11 exchanges use public APIs without authentication.

### Future Sources Requiring Keys
- **The Graph**: API key for >1K queries/day
- **Alpaca**: API key (free tier available)
- **Polygon.io**: API key (paid)
- **Dune Analytics**: API key (paid)
- **OANDA**: Account required
- **Interactive Brokers**: Trading account required

**Strategy**: Start with free/no-auth sources first, add paid sources later.

---

## Next Steps

1. **Test current 3 parallel archivers** (crypto_cex, stocks, dex)
2. **Add Phase 1 perpetuals** (dYdX, Vertex, GMX, Drift) to DEX archiver
3. **Create Phase 2 spot DEX** archiver (Jupiter, Uniswap, PancakeSwap)
4. **Add Phase 3 regional CEX** (Kraken, Upbit, Crypto.com, Huobi)
5. **Create derivatives archiver** (Deribit, Lyra, Aevo)

**Estimated Timeline**: 12 weeks to reach 30+ exchanges covering 90%+ of global trading volume

---

## Resources & Documentation

### DEX APIs
- **dYdX V4**: https://docs.dydx.exchange/developers/indexer/indexer_api
- **Vertex**: https://docs.vertexprotocol.com/
- **GMX**: https://docs.gmx.io/
- **Jupiter**: https://station.jup.ag/docs/apis/
- **Uniswap**: https://docs.uniswap.org/api/subgraph/overview

### CEX APIs
- **Kraken**: https://docs.kraken.com/rest/
- **Deribit**: https://docs.deribit.com/
- **Crypto.com**: https://exchange-docs.crypto.com/

### Data Providers
- **The Graph**: https://thegraph.com/docs/
- **Polygon.io**: https://polygon.io/docs/
- **Alpaca**: https://docs.alpaca.markets/

### Tools
- **CCXT Library**: Supports 100+ exchanges (may simplify implementation)
- **Web3.py**: For direct blockchain queries
- **Subgrounds**: Python library for The Graph queries

---

## Summary

**Immediate Action**: The current 3-archiver system (CEX crypto, stocks, DEX) is ready to run in parallel via `run_daily_archive.bat`. 

**Next Expansion**: Add 4 perpetual DEXs (dYdX, Vertex, GMX, Drift) to the DEX archiver to cover 90% of decentralized derivatives volume.

**Ultimate Goal**: 50+ sources covering every major market to give Nexus traders maximum data reach.
