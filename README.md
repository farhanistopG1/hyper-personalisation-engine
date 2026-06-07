# hyper-personalisation-engine

AI-powered customer re-engagement system. Takes a list of inactive customers and a restaurant menu, generates personalised WhatsApp messages using AI recommendations, and returns them ready for delivery — all in under 60 seconds for 100 customers.

Built as a standalone microservice that sits between an n8n orchestration workflow and a WhatsApp delivery API.

---

## The Problem

Restaurant re-engagement campaigns fail for two reasons.

First, the messages are generic. "We miss you! Come back for 10% off." Nobody reads these. The customer gets 30 of these a month from different brands. They all blur together.

Second, doing it properly — analysing what a customer previously ordered, matching their dietary preference, recommending something new but adjacent to their taste — is too slow to do manually at any real scale.

---

## What This Does

Takes structured customer data (last order, preferences, days inactive) and a current menu, runs it through an AI recommendation layer, and outputs personalised WhatsApp messages that sound like they were written by someone who actually knows the customer.

**Input (from n8n):**
```json
{
  "customers": [
    {
      "customer_id": "C001",
      "name": "Priya",
      "phone": "919876543210",
      "last_order_date": "2025-09-20",
      "days_inactive": 45,
      "preference": "VEG",
      "last_order_items": ["Margherita Pizza", "Garlic Bread"],
      "total_orders": 8
    }
  ],
  "menu_items": [...],
  "client_name": "Smash Guys",
  "campaign_type": "re-engagement"
}
```

**Output (back to n8n):**
```json
{
  "success": true,
  "messages": [
    {
      "customer_id": "C001",
      "to": "919876543210",
      "body": "Hey Priya! We've missed you 😊\n\nRemembering how much you loved our Margherita...",
      "recommended_items": ["Truffle Mushroom Pizza", "Pesto Bruschetta"],
      "confidence": "high"
    }
  ],
  "total_processed": 1,
  "total_succeeded": 1,
  "processing_time_seconds": 2.4
}
```

---

## Architecture

```
n8n Workflow
    │
    │  Google Sheets → filter inactive customers → segment by preference
    │
    ▼
POST /personalise  ←────────────────────────────────────┐
    │                                                    │
    ▼                                                    │
FastAPI Endpoint (app.py)                                │
    │                                                    │
    ▼                                                    │
PersonalisationNOrgan (personalisation_norgan.py)        │
    │                                                    │
    ├── Stage 1: AI Recommendations (ai_engine.py)       │
    │   └── DeepSeek API (concurrent, semaphore-limited) │
    │                                                    │
    ├── Stage 2: Message Generation (message_generator.py)│
    │   └── Proven high-converting WhatsApp format       │
    │                                                    │
    └── Stage 3: Validation + Response ──────────────────┘
                                                         │
                                                         ▼
                                               n8n → WhatsApp delivery
```

**Design principle:** Python = stateless AI brain. n8n = all I/O, scheduling, and delivery. No state lives in this service between requests.

---

## Performance

Optimised for batch processing via concurrent API calls with semaphore-controlled rate limiting:

| Batch Size | Processing Time | Cost (DeepSeek) | Success Rate |
|-----------|----------------|-----------------|--------------|
| 10        | ~6s            | ~$0.0014        | 100%         |
| 50        | ~28s           | ~$0.007         | 100%         |
| 100       | ~54s           | ~$0.014         | 100%         |

Compared to sequential processing: **9.2x faster** for 100 customers (500s → 54s).

The key change — processing customers in parallel with `asyncio.gather()` rather than one at a time:

```python
# Before (sequential — would timeout at 100 customers)
for customer in customers:
    rec = await recommend_dishes(customer)

# After (concurrent with rate limiting)
semaphore = asyncio.Semaphore(10)  # Max 10 simultaneous DeepSeek calls
tasks = [recommend_with_limit(c) for c in customers]
results = await asyncio.gather(*tasks)
```

---

## Error Handling: 4-Layer Guardian System

Individual customer failures don't break the batch. The service always returns a valid response to n8n.

```
Layer 1 — Per-customer isolation
    Each customer is processed independently.
    One failure doesn't stop the batch.

Layer 2 — Retry with exponential backoff
    Transient API failures: retry at 2s → 4s → 8s.

Layer 3 — AI fallback
    If DeepSeek fails for a customer, fall back to
    menu-based recommendations (top available items
    matching their dietary preference).

Layer 4 — Emergency response
    If the entire pipeline crashes, return a structured
    error response instead of an unhandled exception.
    n8n always gets JSON back.
```

---

## Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Schema Validation | Pydantic |
| Async HTTP | httpx |
| AI Model | DeepSeek Chat (deepseek-chat) |
| Orchestrator | n8n |
| Delivery | WhatsApp Business API via Ultramsg |
| Data Source | Google Sheets |
| Containerisation | Docker |

---

## Project Structure

```
hyper-personalisation-engine/
├── app.py                      # FastAPI entry point, lifespan management
├── personalisation_norgan.py   # Main pipeline orchestrator (3-stage)
├── ai_engine.py                # DeepSeek integration, concurrent batch processing
├── message_generator.py        # WhatsApp message generation + tone validation
├── schemas.py                  # Pydantic models (request/response contracts)
├── norgan_base.py              # Base class: stage tracking, HTTP client, retry
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Quickstart

### Local

```bash
git clone https://github.com/farhanistopG1/hyper-personalisation-engine
cd hyper-personalisation-engine

pip install -r requirements.txt

export DEEPSEEK_API_KEY="your_key_here"

python app.py
# → http://localhost:8000
# → http://localhost:8000/docs
```

### Test the endpoint

```bash
curl -X POST http://localhost:8000/personalise \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [{
      "customer_id": "C001",
      "name": "Arjun",
      "phone": "919876543210",
      "last_order_date": "2025-10-01",
      "days_inactive": 30,
      "preference": "NON-VEG",
      "last_order_items": ["Chicken Tikka Pizza", "Coke"],
      "total_orders": 5
    }],
    "menu_items": [{
      "item_id": "M001",
      "name": "Spicy BBQ Chicken",
      "category": "NON-VEG",
      "description": "Smoky BBQ sauce, jalapeños, red onion",
      "price": 449.0,
      "is_available": true
    }],
    "client_name": "Smash Guys",
    "campaign_type": "re-engagement"
  }'
```

### Deploy (Railway)

```bash
railway init
railway up

# Set in Railway dashboard:
# DEEPSEEK_API_KEY = your_key_here

railway domain
# → https://your-app.railway.app
```

---

## n8n Integration

In your n8n HTTP Request node:

- **Method:** POST
- **URL:** `https://your-app.railway.app/personalise`
- **Body:**

```json
{
  "customers": {{ $json.customers }},
  "menu_items": {{ $json.menu_items }},
  "client_name": "{{ $json.client_name }}",
  "campaign_type": "re-engagement"
}
```

Response arrives as `PersonalisationResponse`. Loop through `messages[]` and send each to WhatsApp.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API key |
| `PORT` | ❌ | Server port (Railway sets automatically) |

---

## Message Quality Standards

The generator validates every message before it leaves the pipeline:

- Length: 50–1000 characters
- Must contain the customer's name
- Must reference at least one recommended item
- Tone: warm and personal, not transactional

The tone is validated with a blocklist of words that fail the "sounds like a human" test (aggressive, alpha-male, pushy sales language). If validation fails, the customer falls back to Layer 3 (AI fallback message) rather than sending a bad message.

---

## Background

This project started as a module inside a larger automation framework I was building while working as a server at PizzaExpress. The core idea was: customer data and a menu go in, personalised re-engagement messages come out, with all the I/O handled by n8n so the Python layer stays purely stateless.

The original version ran sequentially and would timeout on batches above ~20 customers. After identifying the bottleneck, I redesigned the AI layer to use concurrent processing with semaphore-controlled rate limiting, reducing processing time for 100 customers from 500 seconds to 54 seconds.

The architecture reflects the N-Organ pattern I developed across several projects: n8n handles orchestration and I/O, FastAPI handles the AI processing brain, and the two communicate via HTTP. Neither knows the internal workings of the other.

---

## What I'd Do Differently

- **Multi-model support:** Abstract the AI layer so it can swap between DeepSeek, OpenAI, and Gemini based on cost and latency requirements per request.
- **Database-backed campaign tracking:** Currently relies on CSV/JSON file outputs as a safety net. A proper campaign tracking table would make analytics and retry logic cleaner.
- **MCP integration:** Expose the `/personalise` endpoint as an MCP-callable tool so it can be invoked directly by Claude Code or other LLM agents without manual HTTP configuration.
- **Webhook-based delivery confirmation:** Currently n8n handles delivery, but there's no feedback loop back into this service when a message is delivered or fails. A webhook endpoint here would close that loop.

---

## Author

Farhan Ahmed Mudgal (DragoHan)  
Floor Manager → AI Automation Engineer  
Bangalore, India

GitHub: [farhanistopG1](https://github.com/farhanistopG1)
