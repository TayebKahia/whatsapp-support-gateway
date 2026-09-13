# Issue 05: E-Commerce Order Repository & Session State Store
Status: closed

## 1. Description & Behaviour
Implement data repositories for e-commerce backend operations and conversation state management:
1. `OrderRepository`: Provides lookup for customer orders by ID (`#ORD-1001`), shipping carrier, delivery ETA, items, and return eligibility evaluation.
2. `SessionStore`: Persists customer conversation state, maintaining current status (`ACTIVE_BOT`, `ESCALATED_HUMAN`, `CLOSED`), escalation metadata, and multi-turn message transcripts.

## 2. Deliverables
- `src/gateway/repository/order.py`:
  - `OrderRepository` interface with `get_order(order_id: str) -> OrderRecord | None` and `evaluate_return(order_id: str, reason: str) -> dict`.
  - SQLite/In-memory implementation preloaded with realistic seed orders (`#ORD-1001` Shipped, `#ORD-1002` Processing, `#ORD-1003` Delivered).
- `src/gateway/repository/session.py`:
  - `SessionStore` interface: `get_session(phone: str) -> SessionRecord`, `save_session(session: SessionRecord)`, `append_transcript(phone: str, role: str, message: str)`.
  - Enforces 24-hour customer service window timeout.

## 3. Dependencies & Blockers
- **Blocked by**: Issue 01 (Models).
- **Blocks**: Issue 06 (Intent Router & Pipeline).

## 4. Test Acceptance Criteria (TDD)
- `tests/unit/test_order_repository.py`:
  - Successfully retrieves known order `#ORD-1001` with tracking info.
  - Returns `None` for non-existent order.
  - Evaluates return eligibility (e.g. Delivered < 30 days ago is eligible; Processing is not eligible).
- `tests/unit/test_session_store.py`:
  - Creates new session in `ACTIVE_BOT` state upon first lookup.
  - Appending messages maintains chronologically ordered transcript.
  - Correctly resets/closes sessions older than 24 hours.

## Notes & Verification
- Implemented `InMemoryOrderRepository` with order lookups and return eligibility logic.
- Implemented `InMemorySessionStore` with automatic 24-hour customer care window timeout enforcement.
- 41/41 unit/integration tests passing.
- Strict typing and ruff linting 100% clean.

