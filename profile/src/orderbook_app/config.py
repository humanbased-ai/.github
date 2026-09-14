from __future__ import annotations

from dataclasses import dataclass
import os
from urllib.parse import quote


@dataclass(frozen=True)
class AppConfig:
    db_dsn: str

    @staticmethod
    def from_env() -> "AppConfig":
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            password = os.getenv("PGPASSWORD")
            if not password:
                raise ValueError("Set DATABASE_URL or PGPASSWORD; no default database password is supplied")
            host = os.getenv("PGHOST", "db")
            user = quote(os.getenv("PGUSER", "orderbook"), safe="")
            database = quote(os.getenv("PGDATABASE", "orderbook"), safe="")
            dsn = f"postgresql://{user}:{quote(password, safe='')}@{host}:5432/{database}"
        return AppConfig(db_dsn=dsn)
