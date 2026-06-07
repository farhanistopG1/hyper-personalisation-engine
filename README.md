# 💀 HYPER PERSONALISATION N-ORGAN 💀

**AI-powered customer re-engagement system for Pizza Express**

## What is an N-Organ?

**N-Organ** = Hybrid N8N + Python system

- **N8N** handles data orchestration (Google Sheets, APIs, webhooks)
- **Python** handles complex AI logic (recommendations, transformations)
- **Communication** via synchronous HTTP POST (N8N waits for response)

**Golden Rule:** Python = stateless brain with zero memory. No hard-coded config.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        N8N WORKFLOW                         │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐         │
│  │  Google  │───▶│  Filter  │───▶│ Segment      │         │
│  │  Sheets  │    │  Active  │    │ VEG/NON-VEG  │         │
│  └──────────┘    └──────────┘    └──────────────┘         │
│                                          │                  │
│                                          ▼                  │
│                              ┌─────────────────────┐        │
│                              │  HTTP POST Request  │        │
│                              │  (customers + menu) │        │
│                              └─────────────────────┘        │
└─────────────────────────────────────│───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    PYTHON N-ORGAN (Railway)                 │
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  AI Engine       │───▶│  Message Gen     │              │
│  │  (DeepSeek)      │    │  (Friendly Tone) │              │
│  └──────────────────┘    └──────────────────┘              │
│                                   │                         │
│                                   ▼                         │
│                      ┌─────────────────────┐                │
│                      │  HTTP POST Response │                │
│                      │  (formatted msgs)   │                │
│                      └─────────────────────┘                │
└─────────────────────────────────────│───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        N8N WORKFLOW                         │
│                                                             │
│         ┌──────────────┐    ┌──────────────┐               │
│         │  WhatsApp    │───▶│  Log to      │               │
│         │  Delivery    │    │  Sheets      │               │
│         │  (Ultramsg)  │    │              │               │
│         └──────────────┘    └──────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### 1. AI-Powered Recommendations
- **DeepSeek API** integration for cost-effective AI
- Customer history analysis
- Preference matching (VEG/NON-VEG)
- Smart dish recommendations based on past orders

### 2. Personalized Message Generation
- **Warm, friendly, professional tone** ✅
- Sounds like a friend who misses you
- Random intro/outro variations
- Emoji-rich, WhatsApp-optimized

### 3. Message Quality Validation
- Tone validation (NO Andrew Tate language)
- Length validation (50-1000 chars)
- Structure validation (intro, body, outro)

### 4. 4-Layer Guardian Error System
- **Layer 1:** Per-customer failures don't break batch
- **Layer 2:** Retry with exponential backoff
- **Layer 3:** Fallback messages when AI fails
- **Layer 4:** Emergency response (always return something)

---

## Project Structure

```
norgans/hyper_personalisation/
├── app.py                      # FastAPI HTTP endpoint
├── personalisation_norgan.py   # Main N-Organ orchestrator
├── ai_engine.py                # DeepSeek recommendation engine
├── message_generator.py        # Friendly message generation
├── schemas.py                  # Pydantic request/response models
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container config
├── test_local.py               # Python test script
├── test_curl.sh                # Curl test script
└── README.md                   # This file
```

---

## Installation & Setup

### 1. Local Development

```bash
# Navigate to the N-Organ directory
cd copy_grimoire/norgans/hyper_personalisation

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"

# Run the FastAPI app
python app.py

# Server will start on http://localhost:8000
```

### 2. Test Locally

#### Option A: Python Test Script
```bash
python test_local.py
```

#### Option B: Curl Test Script
```bash
./test_curl.sh
```

#### Option C: Manual Curl
```bash
curl -X POST http://localhost:8000/personalise \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [...],
    "menu_items": [...],
    "client_name": "Pizza Express",
    "campaign_type": "re-engagement"
  }'
```

### 3. Deploy to Railway

```bash
# From the hyper_personalisation directory
railway init
railway up

# Set environment variable in Railway dashboard:
# DEEPSEEK_API_KEY = your_key_here

# Get the Railway URL (e.g., https://your-app.railway.app)
railway domain
```

---

## API Reference

### Base URL
- **Local:** `http://localhost:8000`
- **Railway:** `https://your-app.railway.app`

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "service": "Hyper Personalisation N-Organ",
  "status": "running",
  "version": "1.0.0"
}
```

#### `GET /health`
Detailed health status.

**Response:**
```json
{
  "status": "healthy",
  "organ_initialized": true,
  "deepseek_api_configured": true,
  "timestamp": 1234567890.123
}
```

#### `POST /personalise`
Main endpoint for generating personalized messages.

**Request Body:**
```json
{
  "customers": [
    {
      "customer_id": "C001",
      "name": "John Smith",
      "phone": "919876543210",
      "last_order_date": "2024-10-15",
      "days_inactive": 45,
      "preference": "NON-VEG",
      "last_order_items": ["Pepperoni Pizza", "Garlic Bread"],
      "total_orders": 8
    }
  ],
  "menu_items": [
    {
      "item_id": "M001",
      "name": "Margherita Pizza",
      "category": "VEG",
      "description": "Classic tomato and mozzarella",
      "price": 299.0,
      "is_available": true
    }
  ],
  "client_name": "Pizza Express",
  "campaign_type": "re-engagement"
}
```

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "customer_id": "C001",
      "to": "919876543210",
      "body": "Hey John! We've missed you 😊\n\nBased on your last order...",
      "platform": "whatsapp",
      "recommended_items": ["Chicken Alfredo", "Pepperoni Pizza"],
      "confidence": "high"
    }
  ],
  "total_processed": 1,
  "total_succeeded": 1,
  "total_failed": 0,
  "errors": [],
  "processing_time_seconds": 2.45,
  "metadata": {...}
}
```

---

## N8N Integration

### HTTP Request Node Configuration

**Method:** `POST`

**URL:** `https://your-railway-app.railway.app/personalise`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "customers": {{ $json.customers }},
  "menu_items": {{ $json.menu_items }},
  "client_name": "Pizza Express",
  "campaign_type": "re-engagement"
}
```

**Response:**
- N8N receives `PersonalisationResponse`
- Extract `messages` array
- Loop through messages for WhatsApp delivery

---

## Message Tone Guidelines

### ✅ DO (Friendly, Professional, Personal)
- Sound like a friend who knows the customer
- Warm, nostalgic, caring
- Use emojis (😊🍕❤️💚✨)
- Personal greetings with customer name
- "We've missed you!"
- "Your favorite table is waiting"

### ❌ DON'T (Andrew Tate Tone)
- NO "warrior" language
- NO "beast mode" or "grind"
- NO "LISTEN UP, WARRIOR!"
- NO aggressive or commanding tone
- NO "alpha" or "sigma" language

**Example Good Message:**
```
Hey John! We've missed you 😊

Based on your last order, we think you'll love our
Chicken Alfredo and Pepperoni Pizza! 🎉

Come visit us soon! We'd love to see you again 💚
```

**Example Bad Message:**
```
LISTEN UP, WARRIOR! Your slice is waiting 👉
Time to DOMINATE your taste buds!
Get back in the GRIND! 💪
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | ✅ Yes | DeepSeek API key for recommendations |
| `PORT` | ❌ No | Server port (default: 8000, Railway sets automatically) |

---

## Error Handling

The N-Organ uses a **4-Layer Guardian System**:

1. **Per-Customer Layer:** Individual customer failures don't break the batch
2. **Retry Layer:** Exponential backoff for transient errors (2s, 4s, 8s)
3. **Fallback Layer:** Generic messages when AI fails
4. **Emergency Layer:** Always return a valid response to N8N

Even if all customers fail, you'll get:
```json
{
  "success": false,
  "messages": [],
  "total_processed": 10,
  "total_succeeded": 0,
  "total_failed": 10,
  "errors": ["..."],
  "processing_time_seconds": 1.23
}
```

---

## Performance

- **Batch Processing:** Handle 100+ customers efficiently
- **Concurrent AI Calls:** Process customers in parallel
- **Timeout:** 30s per AI request
- **Retry Logic:** 3 attempts with exponential backoff
- **Connection Pooling:** Reuse HTTP connections

**Typical Processing Times:**
- 1 customer: ~2-3 seconds
- 10 customers: ~5-8 seconds
- 100 customers: ~30-45 seconds

---

## Monitoring & Debugging

### Logs

All processing stages are logged:
```
💀 PERSONALISATION N-ORGAN PROCESSING 💀
   Customers: 2
   Menu Items: 6
   Client: Pizza Express

   🧠 Stage 1: Generating AI recommendations...
   ✅ Generated 2 recommendations (3.45s)

   📝 Stage 2: Generating personalized messages...
   ✅ Generated 2 messages (0.12s)

   🔍 Stage 3: Validating message quality...
   ✅ Validated 2 messages (0.05s)

💀 PROCESSING COMPLETE 💀
   ✅ Success: 2/2
   ⏱️  Total Time: 3.62s
```

### Validation Errors

If a message fails validation:
```
   ⚠️  Invalid message for C001: Contains forbidden word 'warrior'
```

---

## Troubleshooting

### Issue: "DEEPSEEK_API_KEY not set"
**Solution:** Export the environment variable:
```bash
export DEEPSEEK_API_KEY="your_key_here"
```

### Issue: "N-Organ not initialized"
**Solution:** Restart the FastAPI app. Check startup logs for errors.

### Issue: "Message validation failed"
**Solution:** Check the tone guidelines. Ensure messages don't contain forbidden words.

### Issue: "All customers failed"
**Solution:**
- Check DeepSeek API key is valid
- Check menu items are not empty
- Check customer data is valid

---

## Next Steps

1. ✅ **Test locally** - Run `python test_local.py`
2. ✅ **Validate tone** - Check generated messages match friendly tone
3. ⏳ **Deploy to Railway** - Get production URL
4. ⏳ **Update N8N** - Configure HTTP Request node with Railway URL
5. ⏳ **Test end-to-end** - Run full N8N workflow
6. ⏳ **Monitor** - Check logs and error rates

---

## Support

For issues or questions:
- Check the logs (detailed error messages)
- Run the test scripts
- Validate request schema matches Pydantic models
- Check environment variables are set

---

**Built with 💀 Shadow Monarch Framework**

*Golden Rule: Python = stateless brain with zero memory.*
