"""
💀 HYPER PERSONALISATION N-ORGAN API 💀

FastAPI endpoint for N8N to call.

Endpoint: POST /personalise
Input: PersonalisationRequest (customers + menu)
Output: PersonalisationResponse (formatted WhatsApp messages)

Golden Rule: Stateless. Zero memory. No client config.
"""

import os
import sys
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Add paths for imports to work
current_dir = Path(__file__).parent.absolute()
grimoire_root = current_dir.parent.parent
if str(grimoire_root) not in sys.path:
    sys.path.insert(0, str(grimoire_root))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Use absolute imports (works for both direct run and uvicorn)
from schemas import (
    PersonalisationRequest,
    PersonalisationResponse,
    ErrorResponse
)
from personalisation_norgan import PersonalisationNOrgan, PersonalisationGuardian


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

organ_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage N-Organ lifecycle

    Startup: Initialize organ
    Shutdown: Cleanup resources
    """
    global organ_instance

    # Startup
    print("\n💀 HYPER PERSONALISATION N-ORGAN STARTING 💀\n")

    # Check for API key
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("⚠️  WARNING: DEEPSEEK_API_KEY not set in environment")
        print("   Set it in Railway or export DEEPSEEK_API_KEY=your_key\n")

    # Initialize organ
    organ_instance = PersonalisationNOrgan(
        runs_dir="./runs",
        deepseek_api_key=deepseek_key
    )

    print("✅ N-Organ initialized and ready")
    print("🔌 Listening for N8N requests on /personalise\n")

    yield

    # Shutdown
    print("\n💀 SHUTTING DOWN N-ORGAN 💀")
    if organ_instance:
        await organ_instance.close()
    print("✅ Cleanup complete\n")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Hyper Personalisation N-Organ",
    description="AI-powered customer re-engagement system (N8N + Python hybrid)",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Hyper Personalisation N-Organ",
        "status": "running",
        "version": "1.0.0",
        "architecture": "N8N + Python hybrid",
        "endpoints": {
            "POST /personalise": "Generate personalized customer messages"
        }
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    return {
        "status": "healthy",
        "organ_initialized": organ_instance is not None,
        "deepseek_api_configured": bool(deepseek_key),
        "timestamp": time.time()
    }


@app.post("/personalise", response_model=PersonalisationResponse)
async def personalise(request: PersonalisationRequest):
    """
    💀 MAIN ENDPOINT 💀

    Generate personalized WhatsApp messages for customers.

    N8N sends:
    - List of customers (with history, preferences)
    - Menu items (filtered by availability)
    - Client metadata

    Python returns:
    - List of formatted WhatsApp messages
    - Success/failure counts
    - Processing metadata

    Process:
    1. AI recommendations (DeepSeek)
    2. Message generation (friendly tone)
    3. Quality validation
    4. Return to N8N
    """
    global organ_instance

    if not organ_instance:
        raise HTTPException(
            status_code=500,
            detail="N-Organ not initialized"
        )

    print(f"\n{'='*60}")
    print(f"💀 NEW PERSONALISATION REQUEST 💀")
    print(f"   Customers: {len(request.customers)}")
    print(f"   Menu Items: {len(request.menu_items)}")
    print(f"   Client: {request.client_name}")
    print(f"{'='*60}\n")

    try:
        # Process with guardian protection
        response = await PersonalisationGuardian.safe_process(
            organ=organ_instance,
            request=request
        )

        return response

    except Exception as e:
        # Should never reach here due to Guardian, but just in case
        print(f"❌ CRITICAL ERROR: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Internal processing error: {str(e)}"
        )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global error handler

    Ensures we always return JSON to N8N
    """
    print(f"\n❌ UNHANDLED ERROR: {str(exc)}\n")

    error_response = ErrorResponse(
        error=str(exc),
        error_type=type(exc).__name__,
        details={
            "path": str(request.url),
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


# ============================================================================
# MAIN (for local testing)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n💀 STARTING HYPER PERSONALISATION N-ORGAN (LOCAL) 💀\n")
    print("🔌 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🧪 Test: POST http://localhost:8000/personalise\n")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
