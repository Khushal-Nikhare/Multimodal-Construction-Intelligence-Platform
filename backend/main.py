import logging
import time
from typing import Optional, Union, Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from schemas.response import UniversalResponse, UniversalMeta
from routers import safety, cracks, planning, valuation, chatbot, site_assistant, weather
from core.ai_service import (
    query_ai as core_query_ai,
    encode_image_to_base64,
    clean_json_response,
    BASE_CONSTRUCTION_SYSTEM_PROMPT,
)

logging.basicConfig(level=logging.INFO)

# ── Centralized Multimodal AI Request Handler (Activity 4.1) ─────────────────
async def query_ai(
    feature: str = "general",
    user_inputs: Optional[Union[Dict[str, Any], str]] = None,
    image_bytes: Optional[bytes] = None,
    image_media_type: str = "image/jpeg",
    system_prompt: Optional[str] = None,
    user_text: Optional[str] = None,
    use_vision: bool = False,
    max_tokens: Optional[int] = None,
    temperature: float = 0.3,
) -> str:
    """
    Centralized, reusable AI request handler in main.py for platform-wide analysis.
    Supports text-only requests (planning, valuation, chat) and multimodal image-and-text
    requests (safety monitoring, crack assessment).
    """
    return core_query_ai(
        feature=feature,
        user_inputs=user_inputs,
        image_bytes=image_bytes,
        image_media_type=image_media_type,
        system_prompt=system_prompt,
        user_text=user_text,
        use_vision=use_vision,
        max_tokens=max_tokens,
        temperature=temperature,
    )


app = FastAPI(
    title="AI-Powered Multimodal Construction Intelligence Platform API",
    description="Backend services for safety monitoring, crack assessment, planning, valuation, and advisory.",
    version="1.0.0"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Feature Routers ──────────────────────────────────────────────────────────
app.include_router(safety.router)
app.include_router(cracks.router)
app.include_router(planning.router)
app.include_router(valuation.router)
app.include_router(chatbot.router)
app.include_router(site_assistant.router)
app.include_router(weather.router)
app.include_router(weather.legacy_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Ms"] = str(round(process_time * 1000, 2))
    return response

@app.get("/health", response_model=UniversalResponse, tags=["System"])
async def health_check():
    """Health check endpoint to verify backend service readiness."""
    return UniversalResponse(
        status="success",
        data={
            "service": "construction-intelligence-backend",
            "environment": settings.ENVIRONMENT,
            "groq_configured": bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here")
        },
        meta=UniversalMeta(
            model_provider="groq"
        )
    )

@app.get("/api/info", response_model=UniversalResponse, tags=["System"])
async def api_info():
    """API metadata and supported module capabilities."""
    return UniversalResponse(
        status="success",
        data={
            "version": "1.0.0",
            "capabilities": [
                "FR-01: Safety Monitoring",
                "FR-02: Structural Crack Analysis",
                "FR-03: Real Estate Valuation",
                "FR-04: Construction Project Planning",
                "FR-05: Construction Knowledge Assistant",
                "FR-06: Construction Chatbot",
                "FR-07: Daily Site Assistant",
                "FR-08: Weather-Aware Advisory",
                "FR-09: Multimodal Input Handling",
                "FR-10: Structured AI Responses"
            ]
        }
    )
