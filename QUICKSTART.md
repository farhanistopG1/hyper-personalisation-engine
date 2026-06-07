# 💀 QUICK START GUIDE 💀

**Get the Hyper Personalisation N-Organ running in 5 minutes**

---

## Step 1: Install Dependencies

```bash
cd /Users/farhanahmedmudgal/Desktop/monster/copy_grimoire/norgans/hyper_personalisation

pip install -r requirements.txt
```

**Dependencies installed:**
- fastapi
- uvicorn
- pydantic
- httpx

---

## Step 2: Set Environment Variable

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

**Get your key at:** https://platform.deepseek.com/

---

## Step 3: Start the Server

### Option A: Using the start script (recommended)
```bash
./start_server.sh
```

### Option B: Manual start
```bash
# Set PYTHONPATH for imports
export PYTHONPATH="/Users/farhanahmedmudgal/Desktop/monster/copy_grimoire:$PYTHONPATH"

# Start with uvicorn
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**You should see:**
```
💀 HYPER PERSONALISATION N-ORGAN STARTING 💀

✅ N-Organ initialized and ready
🔌 Listening for N8N requests on /personalise

INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 4: Test It

**In a new terminal:**

### Option A: Python Test Suite
```bash
python test_local.py
```

### Option B: Curl Test
```bash
./test_curl.sh
```

### Option C: Browser
Open: http://localhost:8000/docs

Try the interactive API docs!

---

## Step 5: Check the Output

You should see messages like:

```
💬 Generated Messages:

   Message 1:
   To: 919876543210
   Recommended: Chicken Alfredo, Pepperoni Pizza
   Body:
   Hey John! We've missed you 😊

   Based on your last order, we think you'll love our
   Chicken Alfredo and Pepperoni Pizza! 🎉

   Come visit us soon! We'd love to see you again 💚
```

**Check the tone:** ✅ Friendly ❌ No "warrior" language

---

## Next: Deploy to Railway

```bash
# Initialize Railway
railway init

# Deploy
railway up

# Set environment variable in Railway dashboard:
# DEEPSEEK_API_KEY = your_key_here

# Get your production URL
railway domain
```

**Production URL:** `https://your-app.railway.app`

---

## Integrate with N8N

**Add HTTP Request Node:**

- **Method:** POST
- **URL:** `https://your-app.railway.app/personalise`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "customers": {{ $json.customers }},
  "menu_items": {{ $json.menu_items }},
  "client_name": "Pizza Express",
  "campaign_type": "re-engagement"
}
```

**Done!** N8N will send data → Python processes → N8N receives messages

---

## Troubleshooting

### "DEEPSEEK_API_KEY not set"
```bash
export DEEPSEEK_API_KEY="your_key"
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in app.py (line: port=8000)
```

### "Connection refused"
Make sure the server is running: `python app.py`

---

## File Structure

```
hyper_personalisation/
├── app.py              ← Start here (main server)
├── test_local.py       ← Test suite
├── test_curl.sh        ← Quick curl tests
├── README.md           ← Full documentation
├── QUICKSTART.md       ← This file
└── requirements.txt    ← Dependencies
```

---

**That's it! You're ready to go. 💀**

For detailed docs, see [README.md](README.md)
