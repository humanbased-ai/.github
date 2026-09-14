from __future__ import annotations

import asyncio
import asyncpg

from orderbook_app.config import AppConfig
from orderbook_app.services.simulated import generate_simulated_update
from orderbook_app.storage.db import init_db, insert_updates


async def connect_pool(dsn: str, attempts: int = 8) -> asyncpg.Pool:
    for attempt in range(attempts):
        try:
            return await asyncpg.create_pool(dsn, min_size=1, max_size=4)
        except (OSError, asyncpg.CannotConnectNowError, asyncpg.ConnectionDoesNotExistError):
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(min(0.25 * 2 ** attempt, 2))
    raise ValueError("attempts must be positive")


async def run_simulated_ingest() -> None:
    config = AppConfig.from_env()
    pool = await connect_pool(config.db_dsn)
    try:
        await init_db(pool)
        await insert_updates(pool, [generate_simulated_update("sim", "ETH/USDT")])
    finally:
        await pool.close()


def main() -> None:
    asyncio.run(run_simulated_ingest())


if __name__ == "__main__":
    main()
