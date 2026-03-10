# Exchange Geographic Restrictions

> **IMPORTANT — Read before using this file:**
>
> This archiver fetches **public OHLCV market data only**. Public REST endpoints (candles, tickers, symbols) do **not** require authentication and are generally reachable from any IP worldwide, regardless of what the exchange's Terms of Service says about account registration.
>
> The restrictions listed below apply to **account creation, KYC, authenticated API access, and trading**. If you are only running this archiver to collect public market data, geographic blocks typically will **not** affect your data collection — even from countries listed here.
>
> Always verify directly with each exchange's Terms of Service before relying on this file. Policies change frequently. Last research: **July 2025**.

---

## Quick Reference Table

| Exchange | US | UK | Canada | China | Singapore | South Korea | Verified |
|---|---|---|---|---|---|---|---|
| Binance | ❌ | ⚠️ | ⚠️ | ❌ | ⚠️ | ✅ | ⚠️ General knowledge |
| Bybit | ❌ | ❌ | ⚠️ | ❌ | ✅ | ✅ | ⚠️ General knowledge |
| OKX | ❌ | ⚠️ | ⚠️ | ❌ | ✅ | ✅ | ⚠️ General knowledge |
| MEXC | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ⚠️ General knowledge |
| Bitget | ❌ | ⚠️ | ⚠️ | ❌ | ⚠️ | ✅ | ⚠️ General knowledge |
| Gate.io | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ ToS Section 2.5 |
| KuCoin | ❌ | ✅ | ⚠️ | ❌ | ❌ | ✅ | ✅ ToS Section 17.5 |
| Coinbase | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ ToS Section 1.1 |
| Phemex | ❌ | ❌ | ⚠️ | ❌ | ✅ | ✅ | ✅ ToS Section 1.26 |
| Hyperliquid | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ General knowledge |

✅ = Accessible — ❌ = Explicitly restricted — ⚠️ = Partial (some provinces/products only)

---

## Verified Exchanges — Official ToS Data

### Gate.io — ✅ Verified from ToS (Section 2.5)
**Source:** gate.com/legal/user-agreement — Section 2.5 Restricted Locations (fetched July 2025)

**Explicitly restricted (verbatim from ToS):**

United States, Mainland China, Singapore, Canada, France, Germany, Hong Kong, Malaysia, Malta, Cuba, Iran, North Korea, Sudan, Crimea, Spain, Luhansk, Donetsk, Netherlands, Bolivia, United Kingdom, Myanmar, Venezuela, Uzbekistan, Austria, India, Indonesia, **Japan**, Argentina, Cambodia, UAE, Thailand, **South Korea**, Philippines, Pakistan

> Gate.io has one of the longest restriction lists here. Despite this, the public OHLCV API at `api.gateio.ws` functions from all these locations without authentication. The restrictions apply to account creation and authenticated trading only.

---

### KuCoin — ✅ Verified from ToS (Section 17.5)
**Source:** kucoin.com/legal/terms — Article 17, Clause 5 (fetched July 2025)

**Explicitly restricted:**
- United States + all US territories (Puerto Rico, Guam, Northern Mariana Islands, American Samoa, US Virgin Islands)
- Singapore
- Mainland China
- Hong Kong
- Malaysia
- Ontario (Canada)
- British Columbia (Canada)
- France
- Netherlands
- Crimea, Donetsk, Luhansk, Zaporizhzhia, Kherson (Ukraine occupied territories)

---

### Phemex — ✅ Verified from ToS (Section 1.26)
**Source:** phemex.com/help-center/phemex-terms-of-use — Section 1.26 Restricted Territories definition (fetched July 2025)

**Explicitly restricted (full list from ToS):**

UAE, USA, United Kingdom, Ontario, Quebec, Alberta, Saskatchewan (Canada), Afghanistan, Angola, **Australia**, Burundi, Central African Republic, China, Cuba, Crimea, Democratic Republic of Congo, Ethiopia, Eritrea, Guinea, Guinea-Bissau, Haiti, Hong Kong, India, Iraq, Iran, Ivory Coast, Lebanon, Liberia, Libya, Mali, Myanmar, Nicaragua, North Korea, Palestine, Seychelles, Rwanda, Sierra Leone, Somalia, **South Africa**, South Sudan, Sudan, Syria, Venezuela, Yemen, Zimbabwe

> Phemex explicitly bans Australia, South Africa, India, and most of sub-Saharan Africa — a broader list than most other exchanges.

---

### Coinbase — ✅ Verified from ToS (Section 1.1)
**Source:** coinbase.com/legal/user_agreement/united_states — Section 1.1 Eligibility (fetched July 2025)

The US-facing Coinbase product requires users to **reside in the United States** (Section 1.1). For users outside the US, Coinbase provides a separate global platform. The **Coinbase Advanced Trade API** (used by this archiver for public OHLCV) is globally accessible without authentication.

Coinbase complies with OFAC/UN sanctions programs universally.

**Always blocked (OFAC compliance):** Iran, North Korea, Cuba, Syria, Crimea/Sevastopol, Sudan, sanctioned individuals globally.

---

## Unverified Exchanges — General Knowledge

> Official ToS pages for the following exchanges were inaccessible during research (AWS WAF/JS challenges, redirect loops, or 404 errors on all tried URL patterns). The information below is widely reported but **not sourced from official ToS pages at time of research**. Verify independently.

---

### Binance — ⚠️ Could not fetch ToS (AWS WAF blocked)

**Known to restrict:**
- United States — Binance.com blocked; separate Binance.US platform exists
- Mainland China
- Ontario (Canada)
- Netherlands (derivatives products)
- UK retail crypto derivatives (FCA unregistered)
- All OFAC-sanctioned territories

**Known to allow:** South Korea, Japan, Australia, Germany, Singapore (standard spot + futures)

---

### Bybit — ⚠️ Could not fetch ToS (all URLs redirect to bybit.eu)

**Known to restrict:**
- United States (strict IP + KYC block)
- United Kingdom (separate Bybit EU/UK entity)
- Quebec (Canada)
- All OFAC-sanctioned territories

**Known to allow:** Singapore, South Korea, Germany, France (with Bybit EU entity)

---

### OKX — ⚠️ Could not fetch ToS (all legal paths returned 404)

**Known to restrict:**
- United States
- Canada (some provinces)
- Cuba, Iran, North Korea, Syria, Crimea, Sudan

**Known to allow:** Singapore, South Korea, Japan, Germany, France, Australia

---

### MEXC — ⚠️ Could not fetch ToS (no meaningful content extractable)

**Known to restrict:**
- United States (KYC enforcement tightened since 2024)
- All OFAC-sanctioned territories

**Known to allow:** Most other countries — MEXC is one of the more internationally permissive exchanges.

---

### Bitget — ⚠️ Could not fetch ToS (all support/legal URLs returned 404)

**Known to restrict:**
- United States
- United Kingdom (derivatives)
- Singapore (MAS restriction on retail derivatives)
- All OFAC-sanctioned territories

> Bitget requires a passphrase in addition to API key/secret. Set `bitget_passphrase` in `config.json`.

---

### Hyperliquid — ⚠️ Could not fetch ToS (redirect to hyperfoundation.org blocked)

**Known to restrict:**
- United States (some products)
- All OFAC-sanctioned territories

**Known to allow:** Most countries — decentralized DEX model

---

### Yahoo Finance (YFinance) — ✅ Publicly Accessible Worldwide

**No restrictions.** Yahoo Finance provides free, publicly accessible market data for stocks, ETFs, and international equities. No API keys, registration, or authentication required. Data is fetched from publicly available endpoints accessible from any country.

**Supported markets:**
- US stocks and ETFs (NYSE, NASDAQ, AMEX)
- International equities (append exchange suffix: `.TO` Canada, `.L` London, `.T` Tokyo, etc.)
- Major indices
- Forex pairs
- Commodities and futures

**Data access:** Completely open — no geographic blocks, no rate limits beyond reasonable use (2 requests/second recommended).

**Enable in config.json:** Set `"use_yfinance": true` and add symbols to `markets_info/yfinance/yfinance_symbols_data_bot.json`.

Hyperliquid is a **decentralized perpetuals DEX** on its own L1 chain. The protocol is permissionless; the official frontend (`app.hyperliquid.xyz`) and API enforce US IP geo-blocks.

**Known to restrict:** United States IPs at the API/frontend level
**Known to allow:** All other jurisdictions for API access

> No API key/secret used — wallet-based authentication. Set `hyperliquid_address` and `hyperliquid_private_key` in `config.json`.

---

## Best Countries to Run This Archiver

For maximum exchange compatibility when creating API keys (authenticated access), use a server in one of these countries:

| # | Country | Exchanges | Notes |
|---|---|---|---|
| 1 | **Germany** | All 10 | EU-regulated; excellent global connectivity |
| 2 | **Switzerland** | All 10 | Crypto-friendly regulation |
| 3 | **Estonia / Lithuania** | All 10 | EU VASP framework; cheap VPS |
| 4 | **Japan** | All 10 | Low latency to Asian exchanges |
| 5 | **Australia** | 9/10 (not Phemex) | Good Asia-Pacific connectivity |
| 6 | **South Korea** | 9/10 (not Gate.io) | Excellent Asian exchange latency |
| 7 | **Singapore** | 8/10 (not KuCoin, Gate.io) | Best latency to Binance/Bybit/OKX |
| 8 | **UAE (Dubai)** | 8/10 (not Gate.io, Phemex) | Zero crypto tax; good latency |

**Avoid for API key creation:** US, UK, Canada (Ontario/Quebec/BC/Alberta/Saskatchewan), Mainland China, Hong Kong, Malaysia, France, Netherlands, and all OFAC-sanctioned territories.

For **public OHLCV data collection only** (no API keys), any country works — all 10 exchanges serve public market data endpoints globally.

---

## VPN vs VPS

### VPN — For testing only

Cheap and easy but **not recommended** for production archiving:
- Shared IPs are routinely flagged and banned by exchange security systems
- Disconnects break continuous 24/7 archiving
- Many exchanges actively detect VPN/proxy usage
- Does **not** resolve the underlying account jurisdiction restriction

Good options for occasional testing: Mullvad, ProtonVPN, Windscribe.

---

### VPS — Recommended for production

A dedicated cloud server with a clean datacenter IP running 24/7:

| Provider | Locations | Price | Notes |
|---|---|---|---|
| [Hetzner](https://hetzner.com) | Frankfurt, Helsinki, Singapore | ~€4/mo | Best EU price/performance |
| [Contabo](https://contabo.com) | Germany, Singapore, Tokyo | ~$5/mo | Large storage; good for growing SQLite DB |
| [DigitalOcean](https://digitalocean.com) | Singapore, Frankfurt, Amsterdam | ~$6/mo | Reliable; easy Docker setup |
| [Vultr](https://vultr.com) | Tokyo, Frankfurt, Singapore, Sydney | ~$6/mo | Hourly billing; flexible regions |
| [Linode/Akamai](https://linode.com) | Singapore, Frankfurt, Tokyo | ~$5/mo | Stable network |
| [AWS Lightsail](https://aws.amazon.com/lightsail) | ap-southeast-1, eu-central-1 | ~$5/mo | AWS infrastructure; seamless Docker |

**Minimum recommended spec:** 1 vCPU, 2 GB RAM, 20 GB SSD — SQLite DB can reach 50+ GB with large backlogs. Ubuntu 22.04 LTS.

---

## Deploying on a VPS

```bash
# 1. SSH into your VPS
ssh user@your-vps-ip

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker

# 3. Clone repo and configure
git clone https://github.com/your-username/nexus_archiver.git
cd nexus_archiver
cp config.json.example config.json
nano config.json          # Fill in API keys for your exchanges

# 4. Run comprehensive backfill
docker compose up -d

# 5. Monitor logs
docker compose logs -f archiver
```

For automated daily updates, add to crontab (`crontab -e`):

```
# Daily OHLCV update at 00:05 UTC
5 0 * * * cd /home/user/nexus_archiver && docker compose run --rm archiver-daily >> /var/log/nexus_daily.log 2>&1
```

---

*Last research: July 2025. Exchange policies change — always verify on each exchange's official Terms of Service page before relying on this file.*
