# WhatsApp Support Gateway

[![CI Pipeline](https://github.com/TayebKahia/whatsapp-support-gateway/actions/workflows/ci.yml/badge.svg)](https://github.com/TayebKahia/whatsapp-support-gateway/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic V2](https://img.shields.io/badge/Pydantic-v2.8+-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 103 Passing](https://img.shields.io/badge/Tests-103%20Passing-brightgreen)](https://github.com/TayebKahia/whatsapp-support-gateway)

> **Commercial-grade, high-concurrency customer support automation for e-commerce brands on WhatsApp. Engineered with sub-30ms webhook acknowledgment, WAMID idempotency, phone-based zero-login identity, multi-package disambiguation, anti-IDOR security challenges, programmatic vector PDF return labels, and stateful human escalation.**

---

## 1. Executive Summary & Architecture

E-commerce businesses losing customer orders over slow WhatsApp response times face two common pitfalls in production:

1. **The Webhook Retry Storm**: LLMs or slow database queries take $> 3$ seconds to reply. Meta's WhatsApp Cloud API times out, aggressively retrying the webhook every 10–20 seconds. This triggers infinite message duplication loops, broken conversational state, and ballooning compute/LLM costs.
2. **The Unguarded Chatbot**: Unconstrained prompt wrappers hallucinate tracking numbers, bypass return eligibility windows, or get stuck in repetitive loops with angry customers. Furthermore, naive bot implementations leak sensitive shipping addresses when an attacker types another customer's order ID (*Insecure Direct Object Reference / IDOR*).

The **WhatsApp Support Gateway** solves both problems with an enterprise-ready, hexagonal architecture:
- **Sub-30ms Ingestion Decoupling**: Validates HMAC-SHA256 signatures, deduplicates inbound messages by WhatsApp Message ID (`WAMID`), enqueues payloads asynchronously, and returns `HTTP 200 OK` to Meta in under 25ms.
- **Phone-Based Zero-Login Identity**: Leverages WhatsApp's protocol-authenticated phone numbers. Customers never need to create accounts, remember passwords, or dig up order numbers to check package status.
- **Multi-Package Disambiguation**: Automatically identifies when a shopper has multiple active shipments (e.g., `#ORD-1004` and `#ORD-1005`) and presents native interactive buttons for instant 1-tap package tracking.
- **Anti-IDOR Security Shield**: If a shopper queries an order placed under a different phone number (such as a gift or shared household account), the gateway demands the last 4 digits of the phone number on file before revealing order details.
- **Automated Returns & Instant Vector PDF Labels**: Evaluates store return policies on delivered packages (`#ORD-1003`) and dynamically generates printable vector PDF shipping labels complete with scannable Code128 barcodes and RMA packing slips.
- **Shopify Admin REST API Integration**: Swappable order repository ports supporting live Shopify store sync (`ShopifyOrderAdapter`) and offline development fixtures.
- **Stateful Human Escalation & Strict Bot Muting**: Dispatches webhook alerts to external helpdesks (Zendesk / n8n), completely mutes the automated bot to eliminate spam, and opens a real-time two-way WebSocket bridge for human agents.
- **Zero-Credential Dual-Pane Cockpit (`/demo`)**: An embedded web cockpit with a simulated WhatsApp phone interface on the left and a live engine telemetry console on the right (speed, HMAC status, bot intent, and real-time server logs).

---

## 2. Architecture & Data Flow

```mermaid
flowchart TD
    subgraph ClientLayer [WhatsApp & Meta Cloud]
        WA[Customer on WhatsApp]
        MetaAPI[Meta WhatsApp Cloud API v20.0+]
        WA <-->|End-to-End Encrypted Messages| MetaAPI
    end

    subgraph GatewayCore [WhatsApp Support Gateway Service]
        subgraph IngestionBoundary [1. Ingestion Boundary (Sub-30ms)]
            WH[POST /webhook]
            HMAC[HMAC SHA-256 Validator]
            Idem[Idempotency Filter (WAMID)]
        end

        subgraph QueueLayer [2. Asynchronous Queue Layer]
            QueuePort[QueuePort Interface]
            InProcQueue[In-Process Async Worker Pool]
            RedisQueue[Redis Streams Consumer Group]
        end

        subgraph CoreEngine [3. Core Conversational Engine]
            Processor[Event Processor & Identity Resolver]
            Router[Intent Router]
            SM[Session State Machine]
            ToolAgent[Bounded Tool Agent]
        end

        subgraph Repositories [4. Data Adapters & PDF Generator]
            OrderRepo[(Order Repository)]
            ShopifyAdapter[Shopify Admin REST API]
            SessionStore[(Session Store)]
            PDFGen[ReportLab Vector PDF Generator]
        end

        subgraph OutboundBoundary [5. Outbound Channels & Human Takeover]
            ChannelPort[WhatsAppChannelPort]
            MetaChannel[Meta Graph API Channel]
            MockChannel[Mock Test Channel]
            WSOperator[WebSocket Human Operator Desk]
            EventWebhook[Outbound Event Dispatcher (n8n/Zendesk)]
        end
    end

    MetaAPI -->|Inbound Webhook Event| WH
    WH --> HMAC
    HMAC -->|Valid Signature| Idem
    Idem -->|Unique WAMID| QueuePort
    QueuePort -.-> InProcQueue
    QueuePort -.-> RedisQueue
    WH -->|HTTP 200 OK (< 25ms)| MetaAPI

    InProcQueue --> Processor
    RedisQueue --> Processor

    Processor --> Router
    Processor <--> SM
    SM <--> SessionStore

    Router --> ToolAgent
    ToolAgent <--> OrderRepo
    ToolAgent <--> ShopifyAdapter
    ToolAgent --> PDFGen

    Router --> ChannelPort
    ChannelPort -.-> MetaChannel
    ChannelPort -.-> MockChannel
    MetaChannel -->|Outbound Text / Buttons / Documents| MetaAPI

    SM -->|State: ESCALATED_HUMAN| EventWebhook
    EventWebhook -->|Webhook POST| WSOperator
    WSOperator <-->|2-Way Live WebSocket| ChannelPort
```

---

## 3. Core Capabilities & Customer Scenarios

| Customer Scenario | Real-World Problem | Gateway Technical Resolution |
| :--- | :--- | :--- |
| **1. Single Order Auto-Lookup** | Customers hate digging through emails for tracking numbers. | WhatsApp caller ID matches the order database. Tapping **Track Order** returns live FedEx tracking in under 1 second without typing. |
| **2. Conversational Memory** | Customers ask vague follow-ups like *"Can I return it?"*. | The session state machine maintains active order context. If the item is still in transit, it politely explains store return policy. |
| **3. Multi-Package Customer** | Shoppers with multiple active packages get confused by single-order responses. | Gateway detects 2 active packages (`#ORD-1004` & `#ORD-1005`) and sends interactive buttons for 1-tap disambiguation. |
| **4. Brand-New Customer (0 Orders)** | Unknown numbers message support looking for help. | Graceful fallback informs the user that no orders match this phone number, prompting for an order number or human agent. |
| **5. Gift / Cross-Phone (Anti-IDOR)** | Shoppers query an order placed under a spouse's phone or gift recipient. | Anti-IDOR security shield halts the query and demands the last 4 digits of the phone number on file (`6543`) before revealing details. |
| **6. Delivered Return & PDF Label** | Returns require manual agent review and label printing delays. | Delivered package (`#ORD-1003`) is verified for return eligibility. The bot immediately renders a downloadable vector PDF label with a Code128 barcode. |
| **7. Live Shopify Sync** | E-commerce stores need real-time data from their existing Shopify backends. | `ShopifyOrderAdapter` queries the Shopify Admin REST API, extracting real-time line items, prices, and fulfillment stages. |
| **8. Human Takeover & 2-Way Chat** | Angry or complex customer requests require human empathy. | Typing `human` mutes the bot immediately (preventing bot spam) and connects the conversation to a live 2-way operator console. |

---

## 4. Quickstart & Installation

### Prerequisites
- **Python**: 3.11, 3.12, or 3.13
- **uv** (recommended) or standard `pip`
- **Docker & Docker Compose** (optional, for containerized deployment)

---

### Option A: Local Run via `uv` (Recommended)

[`uv`](https://github.com/astral-sh/uv) is an ultra-fast Python package manager that manages virtual environments and dependencies automatically.

```bash
# 1. Clone the repository and navigate to the project directory
git clone https://github.com/your-username/whatsapp-support-gateway.git
cd whatsapp-support-gateway

# 2. Configure environment
cp .env.example .env

# 3. Install dependencies & development tools
uv sync --all-extras

# 4. Run the complete automated test suite (103 tests)
uv run pytest

# 5. Start the Gateway Development Server
uv run uvicorn gateway.main:app --reload --port 8000
```

Once running, navigate to:
- **Interactive Dual-Pane Simulator**: [http://localhost:8000/demo](http://localhost:8000/demo)
- **System Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Option B: Terminal-Based CLI Simulator

Test conversational flows and order lookups directly in your terminal without opening a web browser:

```bash
uv run demo
# or
uv run simulator
```

**Example CLI Interaction:**
```text
============================================================
  WHATSAPP SUPPORT GATEWAY - TERMINAL SIMULATOR
  Type your message, 'human' to escalate, or 'exit' to quit.
============================================================

👤 You (+15551234567): Where is my package?
🤖 Bot (16.2ms):
📦 Order Status: #ORD-1001
• Status: SHIPPED
• Carrier: FedEx (Tracking #: TRK-987654)
• Est. Delivery: 2026-09-15
• Items: Wireless Noise-Canceling Headphones ($189.50)

👤 You (+15551234567): Can I return it?
🤖 Bot (14.8ms):
Order #ORD-1001 is currently in transit. Items must be delivered before a return can be initiated.
```

---

### Option C: Containerized Run with Docker Compose

Deploy the complete stack—including the Gateway service and a Redis container with persistent streams—in a single command:

```bash
docker compose up -d
```

Verify service health:
```bash
# Check running containers
docker compose ps

# Check API health endpoint
curl http://localhost:8000/health
# {"status":"healthy","environment":"development","whatsapp_provider":"mock"}
```

To stop the containers:
```bash
docker compose down
```

---

## 5. Testing & Code Rigor

Every component in this repository is built test-first following strict test-driven development (TDD), full type safety, and clean linting standards.

```bash
# 1. Run all 103 automated tests (unit + integration)
uv run pytest -v

# 2. Strict type verification across all source files (mypy)
uv run mypy src tests

# 3. Linter & code formatting check (ruff)
uv run ruff check .
```

### Test Suite Breakdown (103 Tests)
- **Unit Tests (`tests/unit/`)**:
  - `test_webhook_handshake.py`: Hub verification challenge & query token verification.
  - `test_signature.py`: HMAC-SHA256 signature validation, tampering rejection, replay defense.
  - `test_idempotency.py`: WAMID cache deduplication preventing Meta webhook retry storms.
  - `test_phone_verification.py`: Anti-IDOR 4-digit PIN challenge and order ownership protection.
  - `test_interactive_buttons.py`: Multi-package disambiguation and button payload dispatch.
  - `test_pdf_generator.py`: ReportLab vector return label rendering and Code128 barcode validation.
  - `test_multiturn_memory.py`: Context retention across conversational turns (e.g., *"Can I return it?"*).
  - `test_shopify_adapter.py`: Shopify Admin REST API adapter parsing and fixture fallback.
  - `test_redis_queue.py`: Redis Streams consumer groups, `XADD`, `XREADGROUP`, and acknowledgment.
  - `test_state_machine.py`: Finite state transitions (`MENU` $\rightarrow$ `ACTIVE_BOT` $\rightarrow$ `ESCALATED_HUMAN`).
- **Integration Tests (`tests/integration/`)**:
  - `test_e2e_pipeline.py`: End-to-end inbound webhook to outbound message dispatch pipeline.
  - `test_websocket_chat.py`: Real-time 2-way operator desk connection, agent message injection, and bot silencing.
  - `test_demo_api.py`: Dual-pane web simulator endpoints, session resets, and live event telemetry streams.

---

## 6. API Endpoints Reference

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Gateway health check (environment, provider status, queue mode). |
| `GET` | `/webhook` | Meta WhatsApp Cloud API webhook verification challenge handshake. |
| `POST` | `/webhook` | Inbound WhatsApp webhook ingestion (sub-30ms HMAC validation & queue dispatch). |
| `GET` | `/demo` | Interactive dual-pane web simulator & live engine telemetry cockpit. |
| `POST` | `/demo/simulate` | Dispatches simulated customer messages into the engine. |
| `POST` | `/demo/reset/{phone}` | Resets session state, active order, and chat history for a customer phone. |
| `GET` | `/demo/events` | Server-Sent Events (SSE) stream for real-time engine telemetry. |
| `GET` | `/returns/{return_id}/label.pdf` | Dynamically serves generated vector PDF return shipping labels. |
| `WS` | `/ws/operator/{phone}` | Two-way WebSocket bridge for human operator console. |
| `POST` | `/operator/send` | Dispatches human agent replies directly into the customer's WhatsApp chat. |
| `POST` | `/operator/resolve/{phone}` | Unmutes the automated bot and marks customer inquiry as resolved. |

---

## 7. Configuration & Environment Variables

Copy the example configuration to set up your environment:

```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Gateway HTTP server port. |
| `ENVIRONMENT` | `development` | Environment mode (`development`, `staging`, `production`, `test`). |
| `WHATSAPP_PROVIDER` | `mock` | Outbound channel provider (`mock` or `meta`). |
| `META_APP_SECRET` | `dev_app_secret` | Meta App Secret for validating inbound HMAC-SHA256 signatures. |
| `META_ACCESS_TOKEN` | `""` | System User Permanent Access Token for Meta Graph API v20.0+. |
| `PHONE_NUMBER_ID` | `""` | Meta WhatsApp Business Phone Number ID. |
| `WEBHOOK_VERIFY_TOKEN` | `dev_verify_token` | Custom secret token configured in Meta App Dashboard for webhook verification. |
| `QUEUE_TYPE` | `in_process` | Ingestion queue implementation (`in_process` or `redis`). |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL when `QUEUE_TYPE=redis`. |
| `LLM_PROVIDER` | `mock` | Language model provider (`mock`, `ollama`, `groq`, or `openai`). |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible API base URL (Ollama, vLLM, Groq). |
| `LLM_MODEL` | `qwen2.5:7b` | Model name to query for semantic tool-calling fallback. |
| `ORDER_REPOSITORY_TYPE` | `in_memory` | Order storage engine (`in_memory` or `shopify`). |
| `SHOPIFY_STORE_URL` | `""` | Shopify store domain (`https://store.myshopify.com`). |
| `SHOPIFY_ACCESS_TOKEN` | `""` | Shopify Admin API access token (`shpat_...`). |
| `INTEGRATION_WEBHOOK_URL` | `""` | Outbound escalation webhook destination (n8n, Make, Zapier, Zendesk). |

---

## 8. License

Distributed under the **MIT License**. Free for commercial and private use. See [LICENSE](LICENSE) for details.
