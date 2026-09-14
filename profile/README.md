# Orderbook Ingestion (Binance + OKX)

This package provides parsers, simulated ingest and PostgreSQL storage as a foundation for future **real-time** and **historical** orderbook data ingestion for **ETH/USDT** from **Binance** and **OKX**, store snapshots/updates in **PostgreSQL**, and prepare for future order placement.

## Goals

- Real-time orderbook streaming (WebSocket) for ETH/USDT (spot + perp as needed).
- Historical snapshot pulls (REST) for ETH/USDT.
- Store snapshots and updates in PostgreSQL.
- Prepare for order placement (spot/perp) with API keys.
- Provide simulated data generators for fast tests.
- Docker + docker-compose for easy deployment.

## Required APIs & Credentials

You can prepare these API permissions up front:

### Binance

**Public (no key required)**
- **REST snapshot (spot)**: `GET /api/v3/depth?symbol=ETHUSDT&limit=1000`
- **REST snapshot (perp)**: `GET /fapi/v1/depth?symbol=ETHUSDT&limit=1000`
- **WebSocket stream (spot)**: `wss://stream.binance.com:9443/ws/ethusdt@depth@100ms`
- **WebSocket stream (perp)**: `wss://fstream.binance.com/ws/ethusdt@depth@100ms`

**Private (key required)**
- **Spot order placement**: `POST /api/v3/order`
- **Futures order placement**: `POST /fapi/v1/order`

Required permissions: **Spot Trading** and/or **Futures Trading**; enable **Read** for account and order status.

### OKX

**Public (no key required)**
- **REST snapshot**: `GET /api/v5/market/books?instId=ETH-USDT&sz=400`
- **WebSocket stream**: `wss://ws.okx.com:8443/ws/v5/public` with subscribe message:
  ```json
  {"op": "subscribe", "args": [{"channel": "books", "instId": "ETH-USDT"}]}
  ```

**Private (key required)**
- **Order placement (spot/perp)**: `POST /api/v5/trade/order`

Required permissions: **Trade** and **Read** for account/order status. Ensure passphrase is set.

## Quick Start (uv)

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
```

## Docker

```bash
export ORDERBOOK_DB_PASSWORD="$(openssl rand -hex 32)"
docker compose up --build
```

Preserve the password securely for the database volume's lifetime. PostgreSQL
has no published host port; the app uses the private Compose network and waits
for its healthcheck. The app also retries transient startup connection failures
with a bounded delay. A shared connection pool and batch writes avoid opening a
new connection per update. Prices and sizes retain exact decimal strings in
stored JSON. This entrypoint writes one simulated update; live exchange feeds
and order placement remain unimplemented.

For a local database, set `DATABASE_URL` explicitly. There is no built-in
password. Run `uv run --extra dev pytest`; the optional isolated database test
requires `ORDERBOOK_TEST_DSN` pointing at a disposable administrator database.

## Project Layout

```
src/orderbook_app/
  connectors/         # Binance + OKX parsers
  services/           # Simulated data generators
  storage/            # PostgreSQL helpers
```

## Notes

- This code currently focuses on parsing and schema setup for ETH/USDT orderbooks.
- Use the simulated data generator to validate ingestion logic without API calls.
- Extend `storage/db.py` for historical storage policies (rollups, TTL, etc.).


Compose uses [required variable interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) and [health-based startup ordering](https://docs.docker.com/compose/how-tos/startup-order/). The image installs the committed lock with the tested uv 0.9.28 CLI.
