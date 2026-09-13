# Issue 06: Intent Router, Bounded Tool Agent & Human Escalation State Machine
Status: closed

## 1. Description & Behaviour
Implement the core conversational pipeline connecting inbound messages to business workflows:
1. Fast Intent Router: Matches explicit keywords (`MENU`, `STATUS`, `HUMAN`, `AGENT`) and interactive button clicks instantly with zero token latency.
2. Bounded Tool-Calling Agent: Uses OpenAI-compatible client (supporting Ollama, Groq, or Mock LLM) with Pydantic tool schemas (`LookupOrderArgs`, `CheckReturnEligibilityArgs`).
3. State Machine & Human Escalation:
   - When user requests human support or fails lookup repeatedly, transitions session to `ESCALATED_HUMAN`.
   - **Muting rule**: While in `ESCALATED_HUMAN`, incoming messages are recorded into the transcript but **no automated replies are dispatched**.

## 2. Deliverables
- `src/gateway/engine/router.py`: `IntentRouter` mapping input text/button payloads to intents (`MENU`, `ORDER_QUERY`, `RETURN_QUERY`, `ESCALATION`, `UNKNOWN`).
- `src/gateway/engine/agent.py`: `BoundedToolAgent` executing tools against `OrderRepository`.
- `src/gateway/engine/state_machine.py`: State transition rules for `SessionRecord`.
- `src/gateway/engine/processor.py`: Unified background message worker orchestrating:
  Load Session $\rightarrow$ Check State (if Escalated, record & exit) $\rightarrow$ Route Intent / Execute Tool $\rightarrow$ Update Session $\rightarrow$ Dispatch WhatsApp Reply.

## 3. Dependencies & Blockers
- **Blocked by**: Issue 03 (Queue), Issue 04 (Channel Port), Issue 05 (Order & Session Stores).
- **Blocks**: Issue 07 (Event Webhook), Issue 08 (E2E Demo).

## 4. Test Acceptance Criteria (TDD)
- `tests/unit/test_intent_router.py`:
  - Keyword "menu" routes to main interactive options.
  - "agent" or "human" routes to escalation intent.
  - Interactive button ID `btn_track_order` routes to order prompt.
- `tests/unit/test_tool_agent.py`:
  - When customer query is *"Where is my order ORD-1001?"*, tool agent invokes `lookup_order("ORD-1001")` and synthesizes status response.
  - Deterministic Mock LLM generates consistent tool calls in test environment without network access.
- `tests/unit/test_state_machine.py`:
  - Escalation sets status to `ESCALATED_HUMAN`.
  - Subsequent messages from the same phone number append to transcript but trigger zero outbound messages.

## Notes & Verification
- `IntentRouter` handles button payloads and customer text keywords with zero latency.
- `BoundedToolAgent` validates order schemas and queries `OrderRepository`.
- `SessionStateMachine` and `MessageProcessor` enforce strict bot muting when in `ESCALATED_HUMAN` state.
- 56/56 unit and integration tests passing.
- Strict typing and linting passing with 0 warnings.

