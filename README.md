# WhatsApp Support Gateway (Meta Cloud API + Bounded AI Tool-Calling)

> **Commercial-Grade E-Commerce Customer Support Automation with Sub-30ms Webhook Acknowledgment, WAMID Idempotency, and Stateful Human Escalation.**

[![Tests](https://img.shields.io/badge/tests-94%20passed-brightgreen.svg)](file:///home/kahia-tayeb/Freelance/projects/whatsapp-support-gateway/tests)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-e92063.svg)](https://docs.pydantic.dev/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](file:///home/kahia-tayeb/Freelance/projects/whatsapp-support-gateway/Dockerfile)

---

## 1. Executive Summary

E-commerce businesses losing customer orders over slow WhatsApp response times face two common pitfalls:
1. **The Webhook Retry Storm**: LLMs or slow database queries take $> 3$ seconds to answer. Meta Cloud API times out and retries the webhook, triggering infinite duplicate messages and wasted compute costs.
2. **The Unguarded Chatbot**: Unconstrained prompt wrappers hallucinate delivery dates, fail on return policies, or argue with angry customers without human intervention.

The **WhatsApp Support Gateway** solves both problems with an enterprise architecture:
- **Sub-30ms Ingestion Decoupling**: Validates HMAC-SHA256 signatures, deduplicates via WhatsApp Message ID (`WAMID`), enqueues messages asynchronously, and returns `HTTP 200 OK` in under 30ms.
- **Distributed Redis Streams**: Horizontal worker pool scaling across container replicas via Redis Streams and Consumer Groups (`XADD`, `XREADGROUP`, `XACK`).
- **Real-Time 2-Way WebSocket Human Chat**: Operator console (`/ws/operator/{phone}`) enabling live agent takeover, two-way WhatsApp chat dispatch, and customer message broadcasting.
- **WhatsApp Read Receipts & Typing Indicators**: Instant `status: "read"` Graph API signals (blue ticks) and realistic typing bubble animations.
- **Programmatic PDF Return Labels**: Vector shipping labels & RMA packing slips generated via `reportlab` with scannable Code128 barcodes served dynamically.
- **Multi-Backend E-Commerce Ports**: Swappable order repositories including `ShopifyOrderAdapter` (Shopify Admin REST API + offline fixtures) and `InMemoryOrderRepository`.
- **Anti-IDOR Security Challenge**: 4-digit phone verification challenge preventing unauthorized cross-customer order queries.
- **Zero-Credential Interactive Cockpit**: Features an embedded dual-pane web simulator (`/demo`) with an authentic WhatsApp phone mockup on the left and a live engine telemetry console on the right.

---

## 2. Architecture & Data Flow

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

## 3. Quickstart & Interactive Demo

### Option A: Local Run via `uv` (Recommended)

```bash
# 1. Clone & enter project
cd projects/whatsapp-support-gateway

# 2. Sync dependencies & run tests
uv sync --all-extras
uv run pytest tests/

# 3. Launch Gateway Server
uv run uvicorn gateway.main:app --reload --port 8000
```
Open **[http://localhost:8000/demo](http://localhost:8000/demo)** in your browser to access the **Interactive WhatsApp Phone Simulator & Real-Time Engine Cockpit**.

---

### Option B: Interactive Terminal Simulator

Test conversation flows directly from your shell without launching a web server:
```bash
uv run demo
```
Sample interaction:
```text
👤 Customer: Where is my order #ORD-1001?

🤖 WhatsApp Bot (18.4ms):
 📦 Order Status: #ORD-1001
 • Status: SHIPPED
 • Carrier: FedEx
 • Tracking #: TRK-987654
 • Est. Delivery: 2026-09-15
 • Items: Wireless Noise-Canceling Headphones
```

---

### Option C: Containerized Deployment via Docker Compose

```bash
docker compose up -d
```
Visit `http://localhost:8000/demo` or query health:
```bash
curl http://localhost:8000/health
# {"status":"healthy","environment":"development","whatsapp_provider":"mock"}
```

---

## 4. Production Configuration (`.env`)

To connect to live Meta WhatsApp Cloud API credentials in production:

```ini
# Server Config
PORT=8000
ENVIRONMENT=production

# Meta WhatsApp Cloud API Credentials
WHATSAPP_PROVIDER=meta
META_APP_SECRET=your_meta_app_secret_here
META_ACCESS_TOKEN=your_system_user_access_token_here
PHONE_NUMBER_ID=your_meta_phone_number_id_here
WEBHOOK_VERIFY_TOKEN=your_secure_random_verify_token

# AI / Open-Weight Model Provider
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b

# External Automation Webhook (n8n / Zapier)
INTEGRATION_WEBHOOK_URL=https://n8n.yourdomain.com/webhook/escalation
```

---

## 5. Tailored Upwork Proposal Snippet

When bidding on client contracts seeking WhatsApp API chatbots or customer service automation, use this battle-tested proposal:

```markdown
Hi [Client Name],

I noticed your job post regarding WhatsApp Business API integration and customer service automation.

Most WhatsApp bots fail in production for two reasons:
1. Webhook Timeouts: Meta requires an HTTP 200 OK response within 3 seconds. When backend CRM lookups or AI responses take longer, Meta retries, resulting in duplicate message spam to your customers.
2. Uncontrolled AI: Standard prompt wrappers hallucinate order statuses and cannot safely execute database lookups or respect 24-hour customer care windows.

To solve this, I architect WhatsApp support gateways using an asynchronous ingestion queue (guaranteeing sub-30ms webhook acknowledgments) and schema-bounded tool calling for database lookups (order status, fulfillment, returns). When customers ask for a human or report critical issues, the system automatically mutes the bot, logs the transcript, and fires an event to your helpdesk or n8n/Zapier workflows.

I have already built and containerized a live, tested reference implementation matching this exact architecture:
- GitHub: [Your Portfolio Link]
- Stack: Python (FastAPI), Meta Graph API v20.0+, Pydantic V2, Redis Streams, WebSocket Human Takeover, ReportLab PDF, Docker.
- Test Coverage: 94 automated unit & integration tests covering HMAC signature verification, WAMID deduplication, Redis streams, real-time WebSockets, and stateful human escalation.

I can have your WhatsApp API integration, automated order routing, and helpdesk handoff operational in days. 

Are you available for a quick 10-minute call to discuss your current backend systems and customer messaging volume?

Best regards,
[Your Name]
```
