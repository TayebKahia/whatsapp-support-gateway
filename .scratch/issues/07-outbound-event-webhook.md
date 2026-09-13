# Issue 07: Low-Code Outbound Event Webhook (n8n / Zapier)
Status: closed

## 1. Description & Behaviour
Implement an outbound HTTP webhook dispatcher that fires structured events to external automation platforms (such as n8n, Make, or Zapier) when notable lifecycle events occur—specifically when a customer session transitions to `ESCALATED_HUMAN`.

## 2. Deliverables
- `src/gateway/events/dispatcher.py`: `OutboundEventDispatcher`
  - Reads `INTEGRATION_WEBHOOK_URL` from settings.
  - Formats `EscalationEventPayload` with customer phone, escalation reason, timestamp, and last 5 messages from the transcript.
  - Delivers POST request asynchronously without blocking customer conversation processing.
  - Implements retries with backoff on network failures.
- Wire `OutboundEventDispatcher` into `src/gateway/engine/processor.py` upon escalation.

## 3. Dependencies & Blockers
- **Blocked by**: Issue 06 (Intent Router & State Machine).
- **Blocks**: Issue 08 (E2E Integration & Demo).

## 4. Test Acceptance Criteria (TDD)
- `tests/unit/test_event_dispatcher.py`:
  - When `INTEGRATION_WEBHOOK_URL` is empty, dispatch skips gracefully with no errors.
  - When configured, sends valid `EscalationEventPayload` matching schema.
  - Mocked HTTP server verifies payload contents and headers (`Content-Type: application/json`).
  - Network timeout in event dispatcher does not crash the message processing pipeline.

## Notes & Verification
- `OutboundEventDispatcher` implemented with non-blocking async execution, retries, and network fault tolerance.
- Formats `EscalationEventPayload` containing conversation snippet and escalation metadata.
- 59/59 tests passing, strict mypy and ruff clean.

