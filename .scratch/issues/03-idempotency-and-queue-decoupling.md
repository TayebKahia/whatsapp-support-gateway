# Issue 03: Idempotency Store & Sub-30ms Asynchronous Ingestion Queue
Status: closed

## 1. Description & Behaviour
Decouple inbound webhook ingestion from background message processing to satisfy Meta's $< 3\text{s}$ SLA:
1. `IdempotencyStore`: Caches incoming `WAMID` values. If a message ID was already processed, discard duplicates and return `200 OK` immediately.
2. `QueuePort` & `InProcessAsyncQueue`: Asynchronous event channel using `asyncio.Queue` and worker pool.
3. Fast Acknowledgment: `POST /webhook` enqueues the normalized `InboundMessageEvent` and responds with `HTTP 200 OK` in $< 30\text{ms}$.

## 2. Deliverables
- `src/gateway/repository/idempotency.py`: `IdempotencyStore` interface with `is_processed(wamid: str) -> bool` and `mark_processed(wamid: str, ttl_seconds: int = 86400)`. Implement in-memory cache and SQLite-backed persistent store.
- `src/gateway/queue/base.py`: Abstract `QueuePort` Protocol defining `enqueue(event: InboundMessageEvent)` and worker lifecycle.
- `src/gateway/queue/in_process.py`: `InProcessAsyncQueue` implementing `QueuePort` with background task consumption.
- Update `src/gateway/api/webhook.py`: Connect signature check $\rightarrow$ payload normalization $\rightarrow$ idempotency check $\rightarrow$ enqueue $\rightarrow$ immediate `200 OK`.

## 3. Dependencies & Blockers
- **Blocked by**: Issue 01 (Models), Issue 02 (Webhook Security).
- **Blocks**: Issue 06 (Intent Router & Pipeline).

## 4. Test Acceptance Criteria (TDD)
- `tests/unit/test_idempotency.py`:
  - First encounter of `wamid` returns `is_processed == False`.
  - Marking `wamid` processed causes subsequent calls to return `True`.
  - Expiry/TTL cleanup functions correctly.
- `tests/unit/test_queue.py`:
  - Enqueueing an event dispatches to a registered worker callback asynchronously.
- `tests/integration/test_webhook_ingestion.py`:
  - `POST /webhook` with valid signature and payload returns `200 OK` in $< 30\text{ms}$.
  - Re-sending the identical payload returns `200 OK` without triggering another worker job.

## Notes & Verification
- `IdempotencyStore` implemented with both `InMemoryIdempotencyStore` and persistent `SqliteIdempotencyStore`.
- `InProcessAsyncQueue` decouples ingestion from execution and guarantees background worker execution.
- Integration test verifies sub-30ms webhook acknowledgment and drops duplicate `wamid` deliveries.
- 26/26 tests passing, strict mypy and ruff clean.

