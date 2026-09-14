import json
import os
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import asyncpg
import pytest
from orderbook_app.__main__ import connect_pool
from orderbook_app.config import AppConfig
from orderbook_app.services.simulated import generate_simulated_update
from orderbook_app.storage.db import init_db, insert_updates


def test_database_configuration_has_no_implicit_password(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PGPASSWORD", raising=False)
    with pytest.raises(ValueError, match="no default"):
        AppConfig.from_env()
    monkeypatch.setenv("PGPASSWORD", "a:/@?#%")
    assert "a%3A%2F%40%3F%23%25" in AppConfig.from_env().db_dsn


async def test_transient_connect_failures_retry_but_invalid_auth_does_not(monkeypatch):
    pool = object()
    connect = AsyncMock(side_effect=[OSError("starting"), asyncpg.CannotConnectNowError("starting"), pool])
    sleep = AsyncMock()
    monkeypatch.setattr("orderbook_app.__main__.asyncpg.create_pool", connect)
    monkeypatch.setattr("orderbook_app.__main__.asyncio.sleep", sleep)
    assert await connect_pool("synthetic") is pool
    assert connect.await_count == 3 and sleep.await_count == 2
    connect.side_effect = asyncpg.InvalidPasswordError("invalid")
    with pytest.raises(asyncpg.InvalidPasswordError):
        await connect_pool("synthetic")
    assert sleep.await_count == 2


async def test_batch_storage_preserves_exact_prices_and_sizes():
    dsn = os.getenv("ORDERBOOK_TEST_DSN")
    if not dsn:
        pytest.skip("ORDERBOOK_TEST_DSN requires an isolated PostgreSQL administrator database")
    admin = await asyncpg.connect(dsn)
    database = "orderbook_test_" + uuid.uuid4().hex
    await admin.execute(f'CREATE DATABASE "{database}"')
    pool = None
    try:
        pool = await asyncpg.create_pool(dsn, database=database, min_size=1, max_size=2)
        await init_db(pool)
        update = generate_simulated_update("synthetic", "ETH/USDT")
        update.bids[0].price = Decimal("3000.1234567890123456789")
        update.bids[0].size = Decimal("0.1234567890123456789")
        await insert_updates(pool, [update, update])
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT bids FROM orderbook_updates")
        assert len(rows) == 2
        assert json.loads(rows[0]["bids"])[0] == {"price": "3000.1234567890123456789", "size": "0.1234567890123456789"}
    finally:
        if pool:
            await pool.close()
        await admin.execute(f'DROP DATABASE "{database}"')
        await admin.close()
