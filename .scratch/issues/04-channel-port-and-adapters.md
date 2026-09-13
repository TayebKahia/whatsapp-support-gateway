# Issue 04: WhatsApp Channel Port & Adapters (Meta Cloud & Mock)
Status: closed

## 1. Description & Behaviour
Establish the outbound messaging boundary using Hexagonal Architecture (Ports & Adapters). Enables sending text messages and interactive button menus to WhatsApp users via either Meta's live Cloud API or an in-memory Mock adapter for offline testing.

## 2. Deliverables
- `src/gateway/channel/base.py`: `WhatsAppChannelPort` interface:
  - `send_text(to_phone: str, body: str) -> bool`
  - `send_interactive_buttons(to_phone: str, body: str, buttons: list[dict[str, str]]) -> bool`
- `src/gateway/channel/mock.py`: `MockWhatsAppAdapter` implementing `WhatsAppChannelPort`. Records sent messages into an accessible in-memory list (`sent_messages`) for assertion in tests.
- `src/gateway/channel/meta.py`: `MetaCloudAPIAdapter` implementing `WhatsAppChannelPort`.
  - Sends requests to `https://graph.facebook.com/v20.0/{phone_number_id}/messages`.
  - Formats payloads strictly according to Meta Cloud API requirements.
  - Implements retries with exponential backoff on HTTP 429 / 5xx.

## 3. Dependencies & Blockers
- **Blocked by**: Issue 01 (Models & Settings).
- **Blocks**: Issue 06 (Intent Router & Pipeline).

## 4. Test Acceptance Criteria (TDD)
- `tests/unit/test_mock_channel.py`:
  - Calling `send_text` and `send_interactive_buttons` appends formatted payloads to `sent_messages`.
- `tests/unit/test_meta_channel.py`:
  - Unit tests with `respx` / HTTP mocking verifying correct Graph API payload formatting, headers (`Authorization: Bearer <token>`), and status handling.
  - Verifies retry behavior on simulated transient 503/429 responses.

## Notes & Verification
- `WhatsAppChannelPort` cleanly abstracts Meta Cloud API vs Mock adapter.
- `MockWhatsAppAdapter` enables 100% zero-cost offline tests and simulation.
- `MetaCloudAPIAdapter` strictly validates and formats Graph API v20.0+ payloads with automatic backoff retries.
- 32/32 tests passing cleanly, strict mypy and ruff clean.

