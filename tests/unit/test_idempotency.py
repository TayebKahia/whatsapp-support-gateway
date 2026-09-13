import tempfile
from pathlib import Path

from gateway.repository.idempotency import InMemoryIdempotencyStore, SqliteIdempotencyStore


def test_in_memory_idempotency_store() -> None:
    store = InMemoryIdempotencyStore()
    wamid = "wamid.HBgLMTU1NTk4NzY1NDM="

    assert store.is_processed(wamid) is False
    store.mark_processed(wamid)
    assert store.is_processed(wamid) is True


def test_in_memory_idempotency_multiple_keys() -> None:
    store = InMemoryIdempotencyStore()
    wamid_1 = "wamid.001"
    wamid_2 = "wamid.002"

    store.mark_processed(wamid_1)
    assert store.is_processed(wamid_1) is True
    assert store.is_processed(wamid_2) is False


def test_sqlite_idempotency_store() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_idempotency.db"
        store = SqliteIdempotencyStore(str(db_path))

        wamid = "wamid.SQLITE001"
        assert store.is_processed(wamid) is False
        store.mark_processed(wamid)
        assert store.is_processed(wamid) is True

        # Reopen with same file to verify persistence
        store2 = SqliteIdempotencyStore(str(db_path))
        assert store2.is_processed(wamid) is True
        assert store2.is_processed("wamid.UNKNOWN") is False
