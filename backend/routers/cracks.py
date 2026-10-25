"""
FR-02 – Structural Crack Analysis
Endpoint: POST /api/cracks/analyze
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

router = APIRouter(prefix="/api/cracks", tags=["FR-02: Crack Detection"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

SURFACE_TYPES = {"concrete", "brick_masonry", "plaster", "stone", "other"}

SYSTEM_PROMPT = """You are an expert structural-crack analysis AI assistant.
Your task is to carefully examine the provided image of a structural surface and produce
a structured preliminary crack assessment in JSON format.

Return ONLY valid JSON — no markdown fences, no prose outside the JSON.

The JSON must conform exactly to this schema:

{
  "crack_detected": true,
  "findings": [
    {
      "crack_type": "HAIRLINE | VERTICAL | HORIZONTAL | DIAGONAL_SHEAR | MAP_CRACKING | SPALLING | OTHER",
      "apparent_width_category": "HAIRLINE_LESS_0_2MM | FINE_0_2_TO_1MM | MEDIUM_1_TO_3_MM | WIDE_OVER_3MM | INDETERMINATE",
      "orientation": "VERTICAL | HORIZONTAL | DIAGONAL_45_DEGREE | DIAGONAL_OTHER | IRREGULAR | MAP_PATTERN",
      "preliminary_severity": "COSMETIC | MINOR_NON_STRUCTURAL | MODERATE_STRUCTURAL | SEVERE_STRUCTURAL | CRITICAL | INDETERMINATE",
      "probable_causes": ["<cause 1>", "<cause 2>"],
      "recommended_inspections": ["<action 1>", "<action 2>"]
    }
  ],
  "image_quality_assessment": {
    "clarity": "SUFFICIENT | BLURRY | INSUFFICIENT",
    "lighting": "ADEQUATE | POOR | OVEREXPOSED",
    "recommendation": "<advice on how to improve image quality if needed, or empty string>"
  },
  "disclaimer": "AI crack screening is purely indicative and must never be considered a structural engineering diagnosis or fitness-for-use certification."
}

If no cracks are detected, set "crack_detected" to false and return an empty "findings" array.

Analysis scope:
1. Identify visible crack type and pattern (hairline, vertical, horizontal, diagonal, map cracking, spalling).
2. Estimate crack width category where possible from visual cues.
3. Assess crack orientation and geometry.
4. Determine preliminary severity honestly — do not understate obvious structural concerns.
5. List probable engineering causes (settlement, shrinkage, thermal, overload, corrosion, etc.).
6. Recommend practical follow-up actions (monitoring, gauge installation, professional inspection).
7. Evaluate the image quality and lighting for reliability of your assessment.
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
                        "Accepted: image/jpeg, image/png, image/webp."
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
    summary="Analyse a structural surface image for cracks",
    response_description=(
        "Preliminary crack classification, severity, probable causes, "
        "recommended inspections, and image quality assessment."
    ),
)
async def analyze_cracks(
    image: UploadFile = File(..., description="Structural surface image (JPEG / PNG / WebP, max 10 MB)"),
    surface_type: Optional[str] = Form(
        None,
        description="Surface material: concrete | brick_masonry | plaster | stone | other",
    ),
    structural_element: Optional[str] = Form(
        None,
        description="Structural element: beam | column | shear_wall | slab | non_structural_wall",
    ),
    description: Optional[str] = Form(
        None,
        description="Optional free-text context about the crack or location",
    ),
):
    """
    Accepts a structural surface image with optional context, performs
    AI-assisted crack analysis, and returns preliminary findings.
    """
    request_id = f"req-crk-{uuid.uuid4().hex[:8]}"
    t_start = time.time()

    # --- Validate MIME type ---
    _validate_image(image)

    # --- Validate surface_type if provided ---
    if surface_type and surface_type.lower() not in SURFACE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "error": {
                    "code": "INVALID_SURFACE_TYPE",
                    "message": (
                        f"Unrecognised surface_type '{surface_type}'. "
                        f"Allowed values: {', '.join(sorted(SURFACE_TYPES))}."
                    ),
                },
            },
        )

    # --- Read and size-check image ---
    image_bytes = await image.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error": {
                    "code": "INVALID_IMAGE_PAYLOAD",
                    "message": (
                        f"Uploaded file exceeds the 10 MB limit "
                        f"(received {len(image_bytes):,} bytes)."
                    ),
                    "details": [
                        {
                            "field": "image",
                            "issue": f"File size {len(image_bytes):,} bytes > 10,485,760 bytes",
                        }
                    ],
                },
            },
        )

    # --- Build user-turn text ---
    user_parts = ["Please perform a detailed structural crack analysis of this image."]
    if surface_type:
        user_parts.append(f"Surface material: {surface_type}")
    if structural_element:
        user_parts.append(f"Structural element: {structural_element}")
    if description:
        user_parts.append(f"Additional context: {description}")
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
        logger.exception("AI service error in crack analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "status": "error",
                "error": {
                    "code": "AI_SERVICE_ERROR",
                    "message": "The AI analysis service returned an error. Please retry.",
                    "details": str(exc),
                },
            },
        ) from exc

    # --- Parse & validate structured output (Activity 4.2) ---
    from schemas.contracts import CrackAnalysisData
    from services.output_enforcer import parse_and_validate_ai_response

    safe_fallback = {
        "crack_detected": False,
        "findings": [],
        "image_quality_assessment": {
            "clarity": "INSUFFICIENT",
            "lighting": "ADEQUATE",
            "recommendation": "AI returned an unstructured response. Manual civil review required.",
        },
        "disclaimer": (
            "AI crack screening is purely indicative and must never be considered "
            "a structural engineering diagnosis or fitness-for-use certification."
        ),
    }

    validated_model, was_fallback = parse_and_validate_ai_response(
        raw_response=raw_response,
        schema_cls=CrackAnalysisData,
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
