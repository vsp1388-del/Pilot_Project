"""Wait until both source and target databases accept connections."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2  # noqa: E402

from pilot_framework.config import db_settings  # noqa: E402


def main(timeout: int = 60) -> int:
    deadline = time.monotonic() + timeout
    for role in ("source", "target"):
        settings = db_settings(role)
        while True:
            try:
                psycopg2.connect(**settings.as_dsn_kwargs(), connect_timeout=3).close()
                print(f"{role} database '{settings.dbname}' is ready")
                break
            except psycopg2.OperationalError as exc:
                if time.monotonic() > deadline:
                    print(f"{role} database not reachable: {exc}", file=sys.stderr)
                    return 1
                time.sleep(2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
