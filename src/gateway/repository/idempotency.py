import sqlite3
import time
from typing import Protocol


class IdempotencyStore(Protocol):
    """Port for tracking and deduplicating incoming WhatsApp Message IDs (WAMID)."""

    def is_processed(self, wamid: str) -> bool: ...

    def mark_processed(self, wamid: str, ttl_seconds: int = 86400) -> None: ...


class InMemoryIdempotencyStore:
    """Thread-safe in-memory store for unit tests and single-node development."""

    def __init__(self) -> None:
        self._processed: dict[str, float] = {}

    def is_processed(self, wamid: str) -> bool:
        return wamid in self._processed

    def mark_processed(self, wamid: str, ttl_seconds: int = 86400) -> None:
        self._processed[wamid] = time.time() + ttl_seconds


class SqliteIdempotencyStore:
    """Persistent SQLite-backed idempotency store."""

    def __init__(self, db_path: str = "idempotency.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS idempotency (
                    wamid TEXT PRIMARY KEY,
                    expires_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    def is_processed(self, wamid: str) -> bool:
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM idempotency WHERE wamid = ? AND expires_at > ?",
                (wamid, now),
            )
            return cursor.fetchone() is not None

    def mark_processed(self, wamid: str, ttl_seconds: int = 86400) -> None:
        expires_at = time.time() + ttl_seconds
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO idempotency (wamid, expires_at)
                VALUES (?, ?)
                """,
                (wamid, expires_at),
            )
            conn.commit()
