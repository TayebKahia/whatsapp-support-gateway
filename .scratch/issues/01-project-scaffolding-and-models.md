# Issue 01: Project Scaffolding, Core Models & Settings
Status: closed

## 1. Description & Behaviour
Set up the foundational workspace, dependency management with `uv`, strict type checking configurations (`mypy`, `ruff`), environment settings via `pydantic-settings`, and the complete set of domain and webhook Pydantic V2 data models specified in `SPEC.md`.

## 2. Deliverables
- `pyproject.toml` managed by `uv` with FastAPI, Pydantic V2, Pydantic-Settings, HTTPX, Pytest, Pytest-Asyncio, Ruff, and Mypy.
- `src/gateway/config.py`: `Settings` class loading environment variables with defaults.
- `src/gateway/models/webhook.py`: Meta webhook models (`MetaWebhookPayload`, `MetaEntry`, `MetaChange`, `MetaMessage`, `MetaTextContent`, `MetaInteractiveContent`).
- `src/gateway/models/domain.py`: Internal domain models (`InboundMessageEvent`, `OrderStatus`, `OrderRecord`, `SessionStatus`, `SessionRecord`).
- `src/gateway/models/tools.py`: Bounded tool calling schemas (`LookupOrderArgs`, `CheckReturnEligibilityArgs`, `EscalateToHumanArgs`).
- `src/gateway/models/events.py`: External event schema (`EscalationEventPayload`).

## 3. Dependencies & Blockers
- **Blocked by**: None.
- **Blocks**: Issues 02, 03, 04, 05.

## 4. Test Acceptance Criteria (TDD)
- `tests/unit/test_models.py`:
  - Validates correct parsing of realistic nested Meta WhatsApp JSON payloads into `MetaWebhookPayload`.
  - Validates serialization and deserialization of `InboundMessageEvent`, `OrderRecord`, and `SessionRecord`.
  - Verifies that malformed payloads raise `pydantic.ValidationError`.
- `tests/unit/test_config.py`:
  - Verifies settings load default values and correctly parse overrides from environment variables.
- Type check: `uv run mypy src` runs with zero errors in strict mode.

## Notes & Verification
- Implemented in accordance with TDD: RED tests written first, followed by GREEN implementation and REFACTOR.
- All 10 unit tests passing cleanly in 0.13s.
- `ruff check`, `ruff format --check`, and strict `mypy` passing with 0 warnings.

