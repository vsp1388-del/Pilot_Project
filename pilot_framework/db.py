from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from pilot_framework.config import DbSettings


class Database:
    """Thin read-only wrapper around a psycopg2 connection."""

    def __init__(self, settings: DbSettings):
        self.settings = settings
        self._conn = None

    def connect(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(**self.settings.as_dsn_kwargs())
            self._conn.set_session(readonly=True, autocommit=True)
        return self

    def close(self):
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
        self._conn = None

    @contextmanager
    def _cursor(self):
        self.connect()
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur

    def query(self, sql: str, params=None) -> list[dict]:
        with self._cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def scalar(self, sql: str, params=None):
        with self._cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return None if row is None else next(iter(row.values()))

    def columns(self, table: str, schema: str = "public") -> list[str]:
        rows = self.query(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
            (schema, table),
        )
        return [r["column_name"] for r in rows]
