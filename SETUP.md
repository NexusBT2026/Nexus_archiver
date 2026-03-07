# Setup Guide

Two ways to run Nexus Archiver. Pick one.

---

## Prerequisites (both methods)

### 1. Get the code

```bash
git clone https://github.com/NexusBT2026/Nexus_archiver.git
cd Nexus_archiver
```

### 2. Create your config

```bash
# Windows
copy config.json.example config.json

# macOS / Linux
cp config.json.example config.json
```

Then open `config.json` and fill in your API keys for the exchanges you want to use. You only need keys for exchanges you plan to archive — leave the others as-is.

**Exchange API key fields:**

| Exchange | Required fields | Notes |
|---|---|---|
| Binance | `binance_api_key`, `binance_api_secret` | |
| Bybit | `bybit_api_key`, `bybit_api_secret` | |
| OKX | `okx_api_key`, `okx_api_secret` | |
| MEXC | `mexc_api_key`, `mexc_api_secret` | |
| Bitget | `bitget_api_key`, `bitget_api_secret`, `bitget_passphrase` | Passphrase required |
| Gate.io | `gateio_api_key`, `gateio_api_secret` | |
| KuCoin | `kucoin_api_key`, `kucoin_api_secret`, `kucoin_api_passphrase` | Passphrase required |
| Coinbase | `coinbase_api_key`, `coinbase_api_key_secret` | |
| Phemex | `phemex_api_key`, `phemex_api_secret` | |
| Hyperliquid | `secret_key`, `account_address` | Wallet-based, no traditional API key |

> **Public OHLCV data does not require API keys.** The archiver fetches public market data endpoints — API keys are only needed if you want to extend this project to fetch private account data. You can leave all key fields as `YOUR_*_KEY` placeholders and the archiver will still run.

To disable specific exchanges entirely, set `"use_binance": false` (etc.) in `config.json`.

---

## Method 1 — Native Python

Best for: local development, quick testing, direct log access.

### Requirements

- Python 3.8 or higher
- pip

### Steps

**1. Create a virtual environment**

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> If you use **conda**, you can also do:
> ```bash
> conda create -n nexus_archiver python=3.11
> conda activate nexus_archiver
> ```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the archiver**

```bash
# Full historical backfill (first time — runs for a while)
python -m src.archiver.comprehensive_archiver

# Daily incremental update (subsequent runs)
python -m src.archiver.daily_ohlcv_archiver
```

### What gets created on first run

```
nexus_archiver/
├── archived_data/
│   ├── nexus_archive.db          # SQLite database with all OHLCV data
│   └── archive_config.json       # Auto-generated archiver settings
└── data/
    └── outputs/
        └── api_monitoring/       # API call metrics (auto-created)
```

### Automating daily updates (Windows Task Scheduler)

1. Open **Task Scheduler** → Create Basic Task
2. Trigger: Daily at 00:05
3. Action: Start a Program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `-m src.archiver.daily_ohlcv_archiver`
   - Start in: `C:\Users\Warshawski\nexus_archiver`

Or with a simple batch file (`run_daily.bat`):

```bat
@echo off
cd /d C:\Users\Warshawski\nexus_archiver
call venv\Scripts\activate.bat
python -m src.archiver.daily_ohlcv_archiver >> logs\daily.log 2>&1
```

---

## Method 2 — Docker

Best for: production, VPS deployment, clean isolated environment, no Python install needed.

### Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS)
- Or Docker Engine (Linux)

> On Windows, Docker Desktop must be **running** before any `docker` commands will work.

### Steps

**1. Build the image**

```bash
docker compose build
```

This installs all Python dependencies inside the container. Takes ~40 seconds on first build, cached on subsequent builds.

**2. Run the full backfill**

```bash
docker compose up archiver
```

Logs stream to your terminal. Press `Ctrl+C` to stop.

**3. Run in the background**

```bash
docker compose up -d archiver
```

**4. Check logs**

```bash
docker compose logs -f archiver
```

**5. Run a daily update**

```bash
docker compose run --rm archiver-daily
```

### What gets created

The `archived_data/` folder in your project directory is mounted into the container — data is saved on your host machine, not inside the container. The container is stateless; the data persists.

```
nexus_archiver/
└── archived_data/
    ├── nexus_archive.db          # Your data — persists between runs
    └── archive_config.json
```

### Automating daily updates (crontab on Linux/VPS)

```bash
crontab -e
```

Add:

```
# Daily OHLCV update at 00:05 UTC
5 0 * * * cd /home/user/nexus_archiver && docker compose run --rm archiver-daily >> /var/log/nexus_daily.log 2>&1
```

### Automating daily updates (Windows Task Scheduler)

Same as above but the action is:
- Program: `docker`
- Arguments: `compose run --rm archiver-daily`
- Start in: `C:\Users\Warshawski\nexus_archiver`

---

## Verifying it works

After running either method for a few minutes, confirm data is being stored:

```bash
# Native Python
python -c "
import sqlite3
conn = sqlite3.connect('archived_data/nexus_archive.db')
rows = conn.execute('SELECT exchange, COUNT(DISTINCT symbol) as syms, COUNT(*) as candles FROM ohlcv_data GROUP BY exchange').fetchall()
for r in rows: print(f'{r[0]:15} {r[1]:5} symbols  {r[2]:>10,} candles')
conn.close()
"
```

```bash
# Docker
docker run --rm -v "$(pwd)/archived_data:/app/archived_data" nexus_archiver:latest python -c "
import sqlite3
conn = sqlite3.connect('archived_data/nexus_archive.db')
rows = conn.execute('SELECT exchange, COUNT(DISTINCT symbol) as syms, COUNT(*) as candles FROM ohlcv_data GROUP BY exchange').fetchall()
for r in rows: print(f'{r[0]:15} {r[1]:5} symbols  {r[2]:>10,} candles')
conn.close()
"
```

---

## Exporting data to CSV

```python
from src.archiver.comprehensive_archiver import ComprehensiveArchiver

archiver = ComprehensiveArchiver()
archiver.export_to_csv('hyperliquid', 'BTC', '1h', 'btc_1h.csv')

---

## Customizing the Batch File (Windows)

If you use the provided `run_daily_archive.bat` to automate daily archiving on Windows, you **must edit two lines** to match your own folder and environment:

- `cd /d "C:\Users\Warshawski\nexus_archiver"` (line 10): Change this to the folder where you cloned the repo.
- `call C:\Users\Warshawski\anaconda3\Scripts\activate.bat nexus_archiver` (line 13): Change this to your own Python/conda environment activation command, or remove it if not needed.

Example:

```bat
cd /d C:\Path\To\Your\Repo
call C:\Path\To\Your\PythonEnv\Scripts\activate.bat your_env_name
```

If you use a virtualenv or no environment at all, adjust or remove the activation line as needed. The batch file must be tailored to your system paths for correct operation.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Make sure your venv is activated and `pip install -r requirements.txt` was run |
| `docker: command not found` | Install Docker Desktop and make sure it's running |
| `open //./pipe/dockerDesktopLinuxEngine` error | Docker Desktop is not running — start it and wait ~30s |
| Empty database after running | Check logs for exchange errors; public endpoints work without API keys |
| `PermissionError` in container | Rebuild the image with `docker compose build` (chown fix is in the Dockerfile) |
