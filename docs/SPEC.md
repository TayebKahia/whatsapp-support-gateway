# Technical Specification: WhatsApp Support Gateway
`projects/whatsapp-support-gateway`

---

## 1. Executive Summary & Objective

The **WhatsApp Support Gateway** is a production-grade, resilient microservice that connects WhatsApp Business Cloud API with e-commerce backend systems (orders, inventory, and returns). 

It enforces:
1. **Sub-30ms Webhook Acknowledgment**: Strict decoupling between webhook ingestion and async message processing to satisfy Meta's 3-second SLA and prevent retry storms.
2. **Deterministic Idempotency**: Zero duplicate message processing by tracking Meta's unique WhatsApp Message IDs (`WAMID`).
3. **Hybrid AI Engine**: Fast deterministic keyword/button routing combined with guardrailed open-weight tool-calling (via OpenAI-compatible endpoints like Ollama or Groq) and deterministic fallbacks.
4. **Stateful Human Escalation**: Immediate bot muting when human intervention is requested, preventing rogue bot responses while keeping full customer transcript history.
5. **Low-Code Webhook Integration**: Emits structured outbound events (e.g. `ticket.escalated`) to n8n, Make, or Zapier for team notifications and CRM synchronization.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer [WhatsApp & Meta Cloud]
        WA[Customer on WhatsApp]
        MetaAPI[Meta WhatsApp Cloud API]
        WA <-->|End-to-End Encrypted| MetaAPI
    end

    subgraph GatewayCore [WhatsApp Support Gateway Service]
        subgraph IngestionBoundary [Ingestion Boundary]
            WH[POST /webhook]
            HMAC[HMAC SHA-256 Signature Validator]
            Idem[Idempotency Filter (WAMID)]
        end

        subgraph QueueLayer [Queue & Concurrency Layer]
            QueuePort[QueuePort Interface]
            InProcQueue[In-Process Async Worker Pool]
            RedisQueue[Redis Queue Adapter (Optional)]
        end

        subgraph CoreEngine [Core Conversational Engine]
            Router[Intent Router]
            SM[Session State Machine]
            ToolAgent[Bounded Tool Calling Agent]
            LLMClient[OpenAI-Compatible LLM Client (Ollama/Groq/Mock)]
        end

        subgraph DataLayer [Storage & Backend Adapters]
            SessionDB[(SQLite / In-Memory Session Store)]
            OrderDB[(E-Commerce Order Repository)]
        end

        subgraph OutboundBoundary [Outbound Adapters]
            ChannelPort[WhatsAppChannelPort Interface]
            MetaAdapter[Meta Cloud API Adapter]
            MockAdapter[Mock WhatsApp Test Adapter]
            EventWebhook[Outbound Event Dispatcher (n8n/Slack)]
        end
    end

    subgraph ExternalAutomation [Low-Code Automation & Support]
        N8N[n8n / Make / Zapier Workflows]
        Zendesk[Helpdesk / Human Support Agent]
    end

    MetaAPI -->|POST Webhook Event| WH
    WH --> HMAC
    HMAC -->|Valid| Idem
    Idem -->|New Message| QueuePort
    QueuePort -.-> InProcQueue
    QueuePort -.-> RedisQueue
    WH -->|HTTP 200 OK (< 30ms)| MetaAPI

    InProcQueue --> Router
    RedisQueue --> Router

    Router --> SM
    SM <--> SessionDB
    Router --> ToolAgent
    ToolAgent <--> LLMClient
    ToolAgent <--> OrderDB

    SM -->|State: ESCALATED| EventWebhook
    EventWebhook -->|HTTP POST Event| N8N
    N8N --> Zendesk

    Router --> ChannelPort
    ChannelPort -.-> MetaAdapter
    ChannelPort -.-> MockAdapter
    MetaAdapter -->|POST /messages| MetaAPI
```

---

## 3. Component Boundaries & Deep Modules

| Module Path | Deep Interface / Responsibility | External Dependencies |
| :--- | :--- | :--- |
| `src/gateway/api/webhook.py` | Exposes `GET /webhook` (Meta handshake) and `POST /webhook`. Validates cryptographic HMAC signature and dispatches payload to queue. | FastAPI, Starlette |
| `src/gateway/channel/base.py` | `WhatsAppChannelPort` interface: `send_text`, `send_interactive_buttons`, `verify_signature`. | None (Pure Protocol) |
| `src/gateway/channel/meta.py` | `MetaCloudAPIAdapter`: Produces JSON payload matching Meta Graph API v20.0+, executes HTTP requests with exponential backoff. | `httpx` |
| `src/gateway/channel/mock.py` | `MockWhatsAppAdapter`: Captures outbound messages in an in-memory queue; allows inspecting transcripts during tests. | None |
| `src/gateway/queue/base.py` | `QueuePort` interface: `enqueue(event)`, `start_worker(handler)`, `stop()`. | None (Pure Protocol) |
| `src/gateway/queue/in_process.py` | `InProcessAsyncQueue`: `asyncio.Queue` worker pool with controlled concurrency. | `asyncio` |
| `src/gateway/engine/router.py` | `IntentRouter`: Classifies incoming text into `ORDER_STATUS`, `RETURN_POLICY`, `HUMAN_ESCALATION`, `GREETING`, or `GENERAL_INQUIRY`. | Pydantic |
| `src/gateway/engine/state_machine.py`| `SessionStateMachine`: Manages transitions between `ACTIVE_BOT`, `ESCALATED_HUMAN`, and `CLOSED`. Mutes bot when in `ESCALATED_HUMAN`. | None |
| `src/gateway/engine/agent.py` | `BoundedToolAgent`: Executes structured function calling (`lookup_order`, `check_return_eligibility`) via typed Pydantic tools. | `instructor` / `openai` SDK |
| `src/gateway/repository/order.py` | `OrderRepository`: Query interface for order data (`#ORD-1001`), shipping status, delivery dates, and return eligibility. | SQLite / Memory |
| `src/gateway/repository/session.py`| `SessionStore` & `IdempotencyStore`: Tracks processed `wamid` items and conversation transcripts. | SQLite / Memory |
| `src/gateway/events/dispatcher.py` | `OutboundEventDispatcher`: Delivers JSON webhooks to external endpoints (n8n/Make) when critical events fire. | `httpx` |

---

## 4. Strict Data Schemas (Pydantic V2)

### 4.1 Inbound Webhook Models (Meta Wire Format)

```python
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class WhatsAppMessageType(str, Enum):
    TEXT = "text"
    INTERACTIVE = "interactive"
    BUTTON = "button"
    UNKNOWN = "unknown"


class MetaTextContent(BaseModel):
    body: str


class MetaInteractiveReply(BaseModel):
    id: str
    title: str


class MetaInteractiveContent(BaseModel):
    type: Literal["button_reply", "list_reply"]
    button_reply: MetaInteractiveReply | None = None


class MetaMessage(BaseModel):
    from_number: str = Field(alias="from")
    id: str = Field(description="WhatsApp Message ID (WAMID)")
    timestamp: str
    type: WhatsAppMessageType = WhatsAppMessageType.UNKNOWN
    text: MetaTextContent | None = None
    interactive: MetaInteractiveContent | None = None


class MetaValue(BaseModel):
    messaging_product: Literal["whatsapp"] = "whatsapp"
    metadata: dict[str, str] = Field(default_factory=dict)
    contacts: list[dict[str, str]] = Field(default_factory=list)
    messages: list[MetaMessage] = Field(default_factory=list)


class MetaChange(BaseModel):
    value: MetaValue
    field: Literal["messages"] = "messages"


class MetaEntry(BaseModel):
    id: str
    changes: list[MetaChange] = Field(default_factory=list)


class MetaWebhookPayload(BaseModel):
    object: Literal["whatsapp_business_account"] = "whatsapp_business_account"
    entry: list[MetaEntry] = Field(default_factory=list)
```

### 4.2 Normalized Internal Domain Event

```python
class InboundMessageEvent(BaseModel):
    wamid: str = Field(description="Unique message ID for idempotency")
    sender_phone: str = Field(description="E.164 phone number of user")
    body: str = Field(description="Extracted message text or button payload")
    interactive_id: str | None = Field(default=None, description="Button ID if user clicked a menu")
    timestamp: str
```

### 4.3 Session & Domain Models

```python
class SessionStatus(str, Enum):
    ACTIVE_BOT = "ACTIVE_BOT"
    ESCALATED_HUMAN = "ESCALATED_HUMAN"
    CLOSED = "CLOSED"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderRecord(BaseModel):
    order_id: str
    customer_phone: str
    status: OrderStatus
    carrier: str | None = None
    tracking_number: str | None = None
    estimated_delivery: str | None = None
    items: list[str] = Field(default_factory=list)
    total_amount_usd: float
    order_date: str


class SessionRecord(BaseModel):
    phone_number: str
    status: SessionStatus = SessionStatus.ACTIVE_BOT
    transcript: list[dict[str, str]] = Field(default_factory=list)
    last_interaction_ts: float
    escalation_reason: str | None = None
```

### 4.4 Bounded Tool Calling Schemas

```python
class LookupOrderArgs(BaseModel):
    order_id: str = Field(
        description="The order number extracted from the customer query (e.g. #ORD-1001 or ORD-1001)"
    )


class CheckReturnEligibilityArgs(BaseModel):
    order_id: str = Field(description="Order ID to evaluate for return")
    reason: str = Field(description="Reason provided by customer for the return")


class EscalateToHumanArgs(BaseModel):
    reason: str = Field(description="Explicit reason why human intervention is required")
```

### 4.5 External Event Webhook Schema (for n8n/Zapier)

```python
class EscalationEventPayload(BaseModel):
    event_type: Literal["ticket.escalated"] = "ticket.escalated"
    customer_phone: str
    reason: str
    timestamp: str
    conversation_snippet: list[dict[str, str]]
```

---

## 5. Failure Modes & Resilience Matrix

| Failure Mode | Trigger / Symptom | Mitigation & Handling |
| :--- | :--- | :--- |
| **Invalid Webhook Signature** | Attacker probes endpoint or wrong secret configured. `X-Hub-Signature-256` mismatch. | Reject immediately with `HTTP 401 Unauthorized`. Log warning with IP. Payload discarded. |
| **Duplicate Delivery (At-Least-Once)** | Meta retries webhook due to network jitter. | Look up `wamid` in `IdempotencyStore`. If present, return `HTTP 200 OK` and ignore body. |
| **LLM Inference Outage / Timeout** | Ollama offline, Groq rate-limited (429), or response latency > 5s. | Catch timeout/error; fall back to deterministic pattern-matcher or auto-escalate with polite message: *"I'm having trouble retrieving that. I have flagged this for our team."* |
| **Meta API Rate Limit (429 / 503)** | Burst outbound messages hit Meta Cloud limits. | `MetaCloudAPIAdapter` retries up to 3 times with exponential backoff and randomized jitter (`1s, 2s, 4s`). |
| **Malformed Incoming Payload** | Non-standard Meta event or status update. | Pydantic validation catches schema mismatch; returns `HTTP 200 OK` (so Meta doesn't retry indefinitely) and logs a structured warning. |
| **Customer Spam / Burst** | User sends 10 messages in 3 seconds. | Per-phone locking in the worker queue ensures messages from the same phone are processed sequentially. |

---

## 6. Test Strategy & Acceptance Criteria

### 6.1 Test Pyramid
- **Unit Tests (`tests/unit/`)**:
  - `test_signature_verification.py`: Valid and invalid HMAC signatures.
  - `test_idempotency.py`: Re-submitting identical `wamid` is safely dropped.
  - `test_state_machine.py`: Transitions between `ACTIVE_BOT` $\rightarrow$ `ESCALATED_HUMAN` $\rightarrow$ `CLOSED`. Ensures bot stays muted while escalated.
  - `test_order_repository.py`: Order lookup, missing order numbers, return eligibility rules.
  - `test_intent_router.py`: Keyword detection and fallback routing.
- **Integration Tests (`tests/integration/`)**:
  - `test_webhook_flow.py`: Full end-to-end flow from `POST /webhook` through queue processing to outbound message capture in `MockWhatsAppAdapter`.
  - `test_tool_calling_flow.py`: Inbound message asking *"Where is order ORD-1001?"* correctly invokes `LookupOrderArgs` and dispatches shipping status.
  - `test_escalation_webhook.py`: Triggering escalation sends outbound POST request to configured n8n webhook URL.
- **Resilience & SLA Tests**:
  - `test_webhook_latency.py`: Ingestion endpoint benchmarked to guarantee response time $< 30\text{ms}$ under 50 concurrent requests.

### 6.2 Acceptance Criteria for Done
1. Zero external credential requirement for local testing (`MockWhatsAppAdapter` and `MockLLM` pass full test suite).
2. Clean separation of concerns with 100% typed interfaces (`WhatsAppChannelPort`, `QueuePort`, `OrderRepository`).
3. Single-command startup with `uv` (`uv run pytest` and `uv run demo`).
4. Containerized with `Dockerfile` and `docker-compose.yml`.
