# Issue 02: Cryptographic Webhook Security & Handshake Verification
Status: closed

## 1. Description & Behaviour
Implement the entrypoint HTTP endpoints for Meta's WhatsApp Webhook:
1. `GET /webhook`: Meta's initial handshake verification using `hub.mode`, `hub.challenge`, and `hub.verify_token`.
2. `POST /webhook` signature verification: Cryptographic verification of the `X-Hub-Signature-256` header using HMAC-SHA256 and the configured `META_APP_SECRET`.

## 2. Deliverables
- `src/gateway/security/signature.py`: `verify_meta_signature(raw_payload: bytes, signature_header: str, secret: str) -> bool`. Uses constant-time comparison (`hmac.compare_digest`) to prevent timing attacks.
- `src/gateway/api/webhook.py`:
  - `GET /webhook`: Validates `hub.mode == "subscribe"` and `hub.verify_token == settings.webhook_verify_token`, returning `int(hub.challenge)` as plain text with `HTTP 200 OK`. Returns `HTTP 403 Forbidden` on mismatch.
  - `POST /webhook`: Reads raw request body bytes, checks `X-Hub-Signature-256`, and returns `HTTP 401 Unauthorized` on invalid signature.

## 3. Dependencies & Blockers
- **Blocked by**: Issue 01 (Settings & Models).
- **Blocks**: Issue 03 (Queue & Ingestion).

## 4. Test Acceptance Criteria (TDD)
- `tests/unit/test_signature.py`:
  - Valid HMAC-SHA256 signature returns `True`.
  - Tampered payload or altered secret returns `False`.
  - Missing `sha256=` prefix returns `False`.
- `tests/unit/test_webhook_handshake.py`:
  - `GET /webhook` with valid verify token returns `200` and the challenge string.
  - `GET /webhook` with invalid token returns `403`.
  - `POST /webhook` with invalid signature returns `401`.

## Notes & Verification
- Cryptographic verification implemented using `hmac.compare_digest` to prevent timing attacks.
- GET handshake and POST signature tests pass (21/21 total suite).
- Strict typing (`mypy`) and linting (`ruff`) passing with 0 warnings.

