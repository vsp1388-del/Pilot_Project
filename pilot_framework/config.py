import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class DbSettings:
    host: str
    port: int
    user: str
    password: str
    dbname: str

    def as_dsn_kwargs(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "dbname": self.dbname,
        }


def db_settings(role: str) -> DbSettings:
    """Settings for the `source` or `target` database, read from PILOT_* env vars."""
    role = role.lower()
    if role not in ("source", "target"):
        raise ValueError(f"Unknown database role '{role}', expected 'source' or 'target'")
    return DbSettings(
        host=os.getenv("PILOT_DB_HOST", "localhost"),
        port=int(os.getenv("PILOT_DB_PORT", "5433")),
        user=os.getenv("PILOT_DB_USER", "pilot"),
        password=os.getenv("PILOT_DB_PASSWORD", ""),
        dbname=os.getenv(f"PILOT_{role.upper()}_DB", f"pilot_{role}"),
    )
