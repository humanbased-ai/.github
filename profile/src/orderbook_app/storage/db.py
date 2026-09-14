from __future__ import annotations

import json
from collections.abc import Iterable

import asyncpg
from orderbook_app.models import OrderBookUpdate

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orderbook_updates (
    id bigserial PRIMARY KEY,
    venue text NOT NULL,
    symbol text NOT NULL,
    ts timestamptz NOT NULL,
    bids jsonb NOT NULL,
    asks jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS orderbook_updates_market_time
    ON orderbook_updates (venue, symbol, ts DESC);
"""


async def init_db(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute(CREATE_TABLE_SQL)


async def insert_updates(pool: asyncpg.Pool, updates: Iterable[OrderBookUpdate]) -> None:
    rows = []
    for update in updates:
        payload = update.model_dump(mode="json")
        rows.append((update.venue, update.symbol, update.ts, json.dumps(payload["bids"]), json.dumps(payload["asks"])))
    if not rows:
        return
    async with pool.acquire() as conn:
        await conn.executemany("""
            INSERT INTO orderbook_updates (venue, symbol, ts, bids, asks)
            VALUES ($1, $2, $3, $4, $5)
        """, rows)
