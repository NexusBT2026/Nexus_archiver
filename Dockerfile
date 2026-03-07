# ─────────────────────────────────────────────────────────────
#  Nexus Archiver — Dockerfile
#  Python 3.11-slim on Debian Bookworm
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Metadata
LABEL org.opencontainers.image.title="Nexus Archiver" \
      org.opencontainers.image.description="10-exchange perpetuals OHLCV archiver" \
      org.opencontainers.image.licenses="MIT"

# System dependencies (sqlite3 CLI for inspection, tzdata for cron)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone (override via TZ env var in compose)
ENV TZ=UTC

# Create non-root user for security
RUN useradd -m -u 1000 archiver

WORKDIR /app

# Install Python dependencies first (layer-cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY markets_info/ ./markets_info/

# Pre-create runtime directories and give ownership to archiver user
# (api_rate_monitor.py writes to data/outputs/api_monitoring at runtime)
RUN mkdir -p /app/data/outputs/api_monitoring /app/archived_data \
    && chown -R archiver:archiver /app

# Volumes for persistent data and config (mounted at runtime)
# /app/archived_data  — SQLite database
# /app/config.json    — API keys (never baked into the image)
VOLUME ["/app/archived_data"]

# Switch to non-root user
USER archiver

# Default: run the comprehensive archiver.
# Override CMD in docker-compose or docker run for the daily archiver.
CMD ["python", "-m", "src.archiver.comprehensive_archiver"]
