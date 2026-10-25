"""
FR-01 – Construction Site Safety Monitoring
Endpoint: POST /api/safety/analyze
"""
import json
import logging
import time
import uuid
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from core.ai_service import query_ai
from schemas.response import UniversalError, UniversalMeta, UniversalResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/safety", tags=["FR-01: Safety Monitoring"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

SYSTEM_PROMPT = """You are an expert construction-site safety inspector AI.
Your task is to carefully analyse the provided construction-site image (and any
accompanying textual description) and produce a structured JSON safety report.

Return ONLY valid JSON — no markdown fences, no prose outside the JSON.
The JSON must conform exactly to this schema:

{
  "hazards_identified": [
    {
      "id": "haz-001",
      "category": "PPE_NON_COMPLIANCE | FALL_HAZARD | ELECTRICAL_HAZARD | STRUCTURAL_HAZARD | ENVIRONMENTAL_HAZARD | EQUIPMENT_HAZARD | OTHER",
      "title": "<short title>",
      "severity": "LOW | MEDIUM | HIGH | CRITICAL",
      "description": "<clear description of what was observed>",
      "location_hint": "<approximate image location, e.g. 'center-left foreground'>",
      "corrective_action": "<specific remediation step>"
    }
  ],
  "overall_site_risk": "LOW | MEDIUM | HIGH | CRITICAL",
  "ppe_summary": {
    "compliant_items": ["<item>"],
    "missing_or_non_compliant": ["<item>"]
  },
  "uncertainty_note": "<leave empty string if image is clear; describe image quality issues otherwise>",
  "disclaimer": "This analysis is an AI-assisted screening tool and does not replace a qualified human safety inspection or constitute formal legal compliance certification."
}

Assessment scope:
1. Worker positioning and proximity to hazards.
2. PPE compliance: hard hats, safety vests, gloves, footwear, harnesses.
3. Scaffolding, elevated-work, and fall-protection adequacy.
4. Environmental hazards: debris, open edges, inadequate lighting, wet surfaces.
5. Equipment safety: machinery guard usage, operator positioning.
Assign severity honestly; do not under-report obvious risks.
"""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _validate_image(upload: UploadFile) -> None:
    if upload.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "status": "error",
                "error": {
                    "code": "INVALID_IMAGE_PAYLOAD",
                    "message": (
                        f"Unsupported file type '{upload.content_type}'. "
                        "Accepted types: image/jpeg, image/png, image/webp."
                    ),
                },
            },
        )


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
@router.post(
    "/analyze",
    response_model=UniversalResponse,
    summary="Analyze a construction site image for safety hazards",
    response_description="Structured list of identified hazards, risk level, PPE status, and corrective actions.",
)
async def analyze_safety(
    image: UploadFile = File(..., description="Construction site image (JPEG / PNG / WebP, max 10 MB)"),
    location: Optional[str] = Form(None, description="Textual location hint, e.g. 'Tower B, 4th Floor Slab'"),
    description: Optional[str] = Form(None, description="Optional context about the site or ongoing activity"),
):
    """
    Accepts a construction-site image with optional location and description,
    performs AI-powered safety analysis, and returns structured hazard findings.
    """
    request_id = f"req-safe-{uuid.uuid4().hex[:8]}"
    t_start = time.time()

    # --- Validate MIME type ---
    _validate_image(image)

    # --- Read image bytes ---
    image_bytes = await image.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error": {
                    "code": "INVALID_IMAGE_PAYLOAD",
                    "message": (
                        f"Uploaded file exceeds maximum permissible size of 10 MB "
                        f"(received {len(image_bytes):,} bytes)."
                    ),
                    "details": [{"field": "image", "issue": f"File size {len(image_bytes):,} bytes > 10,485,760 bytes"}],
                },
            },
        )

    # --- Build user text ---
    user_parts = ["Please perform a thorough safety analysis of this construction site image."]
    if location:
        user_parts.append(f"Site Location: {location}")
    if description:
        user_parts.append(f"Additional Context: {description}")
    user_text = "\n".join(user_parts)

    # --- Call AI service ---
    try:
        raw_response = query_ai(
            system_prompt=SYSTEM_PROMPT,
            user_text=user_text,
            image_bytes=image_bytes,
            image_media_type=image.content_type,
        )
    except Exception as exc:
        logger.exception("AI service error in safety analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "status": "error",
                "error": {
                    "code": "AI_SERVICE_ERROR",
                    "message": "The AI analysis service returned an unexpected error. Please retry.",
                    "details": str(exc),
                },
            },
        ) from exc

    # --- Parse & validate structured output (Activity 4.2) ---
    from schemas.contracts import SafetyAnalysisData
    from services.output_enforcer import parse_and_validate_ai_response

    safe_fallback = {
        "hazards_identified": [],
        "overall_site_risk": "MEDIUM",
        "ppe_summary": {"compliant_items": [], "missing_or_non_compliant": []},
        "uncertainty_note": "AI returned an unstructured response. Please inspect the visual scan.",
        "disclaimer": (
            "This analysis is an AI-assisted screening tool and does not replace "
            "a qualified human safety inspection or constitute formal legal compliance certification."
        ),
    }

    validated_model, was_fallback = parse_and_validate_ai_response(
        raw_response=raw_response,
        schema_cls=SafetyAnalysisData,
        fallback_data=safe_fallback,
    )
    analysis_data = validated_model.model_dump()

    latency_ms = round((time.time() - t_start) * 1000, 2)

    return UniversalResponse(
        status="success",
        data=analysis_data,
        meta=UniversalMeta(
            request_id=request_id,
            latency_ms=latency_ms,
            model_provider="groq",
        ),
    )
