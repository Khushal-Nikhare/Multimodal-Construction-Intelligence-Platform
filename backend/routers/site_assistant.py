"""FR-07 – AI-assisted daily construction-site coordination."""
import logging
import time
import uuid
from typing import Any, Dict, Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.ai_service import BASE_CONSTRUCTION_SYSTEM_PROMPT, query_ai
from core.feature_prompts import get_feature_reasoning_prompt
from schemas.contracts import DailySiteAnalysisData
from schemas.response import UniversalMeta, UniversalResponse
from services.output_enforcer import parse_and_validate_ai_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/site-assistant", tags=["FR-07: Daily Site Assistant"])


class DailySiteAssistantRequest(BaseModel):
    activity: str = Field(..., min_length=2, max_length=160)
    labour_count: int = Field(..., ge=1, le=10_000)
    site_condition: Literal["Normal", "Rainy", "Hot", "Windy", "Restricted Access", "Unsafe"] = "Normal"


SITE_ASSISTANT_PROMPT = """You are a construction daily site coordination assistant.
Create a conservative, practical plan for the supplied activity, labour availability, and site condition.
Do not invent measured quantities, engineering approvals, or weather forecasts. Flag conditions that require
the site engineer to stop, resequence, or inspect work. Allocate no more workers across task_breakdown than
the available labour_count.

Return only RFC-8259 JSON with exactly these fields:
{
  "activity": "string",
  "labour_count": 1,
  "site_condition": "string",
  "progress_summary": "string",
  "task_breakdown": [{"task": "string", "priority": "LOW|MEDIUM|HIGH|CRITICAL", "suggested_crew": 0, "execution_notes": "string"}],
  "required_materials_and_equipment": [{"item": "string", "category": "MATERIAL|EQUIPMENT|PPE", "purpose": "string"}],
  "safety_precautions": ["string"],
  "inspection_checklist": ["string"],
  "identified_delays": ["string"],
  "operational_risks": ["string"],
  "recommended_actions": ["string"],
  "disclaimer": "string"
}
"""

EFFECTIVE_SITE_ASSISTANT_PROMPT = (
    f"{BASE_CONSTRUCTION_SYSTEM_PROMPT}\n\n"
    f"{get_feature_reasoning_prompt('site_assistant')}\n\n"
    f"{SITE_ASSISTANT_PROMPT}"
)


def _fallback_plan(payload: DailySiteAssistantRequest) -> Dict[str, Any]:
    condition_risks = {
        "Rainy": "Rain can affect access, electrical safety, and fresh-work protection.",
        "Hot": "Heat can affect worker welfare and concrete placement/curing controls.",
        "Windy": "Wind can affect lifting operations, work at height, and unsecured materials.",
        "Restricted Access": "Restricted access can delay material movement and emergency egress.",
        "Unsafe": "Reported unsafe condition requires site-engineer review before work proceeds.",
    }
    risks = [condition_risks[payload.site_condition]] if payload.site_condition in condition_risks else []
    return {
        "activity": payload.activity,
        "labour_count": payload.labour_count,
        "site_condition": payload.site_condition,
        "progress_summary": f"Prepare and coordinate {payload.activity} with {payload.labour_count} available workers.",
        "task_breakdown": [
            {"task": "Pre-start briefing and work-area preparation", "priority": "HIGH", "suggested_crew": min(2, payload.labour_count), "execution_notes": "Confirm approved method statement, access, and work sequence."},
            {"task": payload.activity, "priority": "HIGH", "suggested_crew": max(0, payload.labour_count - min(2, payload.labour_count)), "execution_notes": "Proceed only after the pre-start checks are complete."},
        ],
        "required_materials_and_equipment": [
            {"item": "Approved tools and equipment", "category": "EQUIPMENT", "purpose": "Carry out the planned activity in accordance with the approved method statement."},
            {"item": "Task-appropriate PPE", "category": "PPE", "purpose": "Protect workers during site operations."},
        ],
        "safety_precautions": ["Conduct a toolbox talk before work begins.", "Verify PPE, access routes, and exclusion zones before releasing the crew."],
        "inspection_checklist": ["Confirm drawings/method statement and permits are current.", "Inspect tools, access, and housekeeping before starting."],
        "identified_delays": [],
        "operational_risks": risks,
        "recommended_actions": ["Assign a competent supervisor to record progress and constraints.", "Escalate changing conditions to the site engineer before resequencing work."],
    }


def _build_plan(payload: DailySiteAssistantRequest) -> tuple[Dict[str, Any], bool]:
    try:
        raw_response = query_ai(
            feature="site_assistant",
            system_prompt=EFFECTIVE_SITE_ASSISTANT_PROMPT,
            user_inputs=payload.model_dump(),
            max_tokens=1_500,
            temperature=0.2,
        )
    except Exception as exc:
        logger.exception("AI service error in daily site assistant: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"status": "error", "error": {"code": "AI_SERVICE_ERROR", "message": "The daily site assistant is temporarily unavailable. Please retry."}},
        ) from exc

    validated, used_fallback = parse_and_validate_ai_response(
        raw_response=raw_response,
        schema_cls=DailySiteAnalysisData,
        fallback_data=_fallback_plan(payload),
    )
    return validated.model_dump(), used_fallback


@router.post("", response_model=UniversalResponse)
@router.post("/analyze", response_model=UniversalResponse, include_in_schema=False)
async def create_daily_site_plan(payload: DailySiteAssistantRequest):
    """Generate a structured, safety-aware daily coordination plan."""
    started_at = time.time()
    data, used_fallback = _build_plan(payload)
    return UniversalResponse(
        status="partial" if used_fallback else "success",
        data=data,
        meta=UniversalMeta(
            request_id=f"req-site-{uuid.uuid4().hex[:8]}",
            latency_ms=round((time.time() - started_at) * 1000, 2),
            model_provider="groq",
        ),
    )
