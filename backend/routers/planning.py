"""
FR-04 – Construction Project Planning & Estimation Router
Endpoints:
  - POST /api/planning/materials  (Material Takeoff Request)
  - POST /api/planning/cost       (Cost Breakdown Request)
  - POST /api/planning/schedule   (Task Schedule Request)
  - POST /api/planning/plan       (Comprehensive Unified Planning Request)
"""
import logging
import time
import uuid
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from schemas.response import UniversalError, UniversalMeta, UniversalResponse
from services.planning_engine import (
    calculate_materials,
    calculate_cost,
    calculate_schedule,
    GRADE_SPECS,
    CITY_COST_MULTIPLIERS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/planning", tags=["FR-04: Project Planning"])


# ── Request Models ────────────────────────────────────────────────────────────

class MaterialTakeoffRequest(BaseModel):
    built_up_area_sqft: float = Field(..., gt=0, description="Built up area in square feet")
    floors: int = Field(1, ge=1, le=120, description="Number of stories/floors")
    construction_grade: str = Field("standard_residential", description="Grade of construction")


class CostBreakdownRequest(BaseModel):
    built_up_area_sqft: float = Field(..., gt=0, description="Built up area in square feet")
    city: str = Field("Bengaluru", description="Project location city")
    construction_grade: Optional[str] = Field("standard_residential", description="Grade of construction")
    contingency_percent: float = Field(7.5, ge=0.0, le=50.0, description="Contingency percentage buffer")


class TaskScheduleRequest(BaseModel):
    built_up_area_sqft: float = Field(..., gt=0, description="Built up area in square feet")
    floors: int = Field(1, ge=1, le=120, description="Number of stories/floors")


class UnifiedPlanRequest(BaseModel):
    built_up_area_sqft: float = Field(..., gt=0, description="Built up area in square feet")
    floors: int = Field(1, ge=1, le=120, description="Number of floors")
    construction_grade: str = Field("standard_residential", description="Grade of construction")
    city: str = Field("Bengaluru", description="Project city")
    contingency_percent: float = Field(7.5, ge=0.0, le=50.0, description="Contingency percentage buffer")
    project_title: Optional[str] = Field(None, description="Optional project title/name")
    description: Optional[str] = Field(None, description="Optional specific context or requirements")


# ── Helper for feasibility checks ────────────────────────────────────────────

def check_structural_feasibility(built_up_area_sqft: float, floors: int) -> Optional[str]:
    """
    Scenario 4.3: Validate realistic area-to-floor proportions.
    E.g. 500 sq.ft total built-up area across 50 floors gives 10 sq.ft per floor footprint.
    """
    avg_area_per_floor = built_up_area_sqft / floors
    if avg_area_per_floor < 80:
        return (
            f"Advisory Warning: High-rise structural density concern. "
            f"Average footprint area per floor ({avg_area_per_floor:.1f} sq.ft for {floors} floors) "
            f"is below standard structural feasibility norms for independent buildings. "
            f"Specialized high-rise structural shear core design required."
        )
    return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/materials", response_model=UniversalResponse)
async def get_materials_takeoff(payload: MaterialTakeoffRequest):
    """
    FR-04.A: Compute material quantities (Cement, Steel, Sand, Aggregate, Bricks).
    """
    t0 = time.time()
    req_id = f"req-mat-{uuid.uuid4().hex[:8]}"

    # Feasibility check
    warning = check_structural_feasibility(payload.built_up_area_sqft, payload.floors)

    data = calculate_materials(
        built_up_area_sqft=payload.built_up_area_sqft,
        floors=payload.floors,
        construction_grade=payload.construction_grade,
    )
    if warning:
        data["feasibility_warning"] = warning

    latency = round((time.time() - t0) * 1000, 2)
    return UniversalResponse(
        status="success",
        data=data,
        meta=UniversalMeta(request_id=req_id, latency_ms=latency, model_provider="parametric_is_cpwd")
    )


@router.post("/cost", response_model=UniversalResponse)
async def get_cost_breakdown(payload: CostBreakdownRequest):
    """
    FR-04.B: Compute approximate construction cost breakdown in INR (₹).
    """
    t0 = time.time()
    req_id = f"req-cst-{uuid.uuid4().hex[:8]}"

    data = calculate_cost(
        built_up_area_sqft=payload.built_up_area_sqft,
        city=payload.city,
        construction_grade=payload.construction_grade or "standard_residential",
        contingency_percent=payload.contingency_percent,
    )

    latency = round((time.time() - t0) * 1000, 2)
    return UniversalResponse(
        status="success",
        data=data,
        meta=UniversalMeta(request_id=req_id, latency_ms=latency, model_provider="parametric_is_cpwd")
    )


@router.post("/schedule", response_model=UniversalResponse)
async def get_task_schedule(payload: TaskScheduleRequest):
    """
    FR-04.C: Generate sequenced construction phases, durations, milestones, and dependencies.
    """
    t0 = time.time()
    req_id = f"req-sch-{uuid.uuid4().hex[:8]}"

    warning = check_structural_feasibility(payload.built_up_area_sqft, payload.floors)

    data = calculate_schedule(
        built_up_area_sqft=payload.built_up_area_sqft,
        floors=payload.floors,
    )
    if warning:
        data["feasibility_warning"] = warning

    latency = round((time.time() - t0) * 1000, 2)
    return UniversalResponse(
        status="success",
        data=data,
        meta=UniversalMeta(request_id=req_id, latency_ms=latency, model_provider="parametric_is_cpwd")
    )


@router.post("/plan", response_model=UniversalResponse)
async def get_unified_plan(payload: UnifiedPlanRequest):
    """
    Consolidated planning endpoint combining Material Takeoff, Cost Estimation,
    Task Scheduling, and Feasibility into a single coordinated response.
    """
    t0 = time.time()
    req_id = f"req-pln-{uuid.uuid4().hex[:8]}"

    warning = check_structural_feasibility(payload.built_up_area_sqft, payload.floors)

    materials_data = calculate_materials(
        built_up_area_sqft=payload.built_up_area_sqft,
        floors=payload.floors,
        construction_grade=payload.construction_grade,
    )

    cost_data = calculate_cost(
        built_up_area_sqft=payload.built_up_area_sqft,
        city=payload.city,
        construction_grade=payload.construction_grade,
        contingency_percent=payload.contingency_percent,
    )

    schedule_data = calculate_schedule(
        built_up_area_sqft=payload.built_up_area_sqft,
        floors=payload.floors,
    )

    data = {
        "project_title": payload.project_title or f"{payload.city} {GRADE_SPECS.get(payload.construction_grade, {}).get('label', 'Residential')} Construction",
        "parameters": {
            "built_up_area_sqft": payload.built_up_area_sqft,
            "floors": payload.floors,
            "construction_grade": payload.construction_grade,
            "city": payload.city,
            "contingency_percent": payload.contingency_percent,
            "description": payload.description or "",
        },
        "feasibility_warning": warning,
        "materials": materials_data["materials"],
        "cost": cost_data,
        "schedule": schedule_data,
        "disclaimer": (
            "Parametric estimates are based on empirical IS 456 & CPWD norms and prevailing city indices. "
            "Site soil conditions, architectural specifications, and contractor market rates require professional review."
        )
    }

    latency = round((time.time() - t0) * 1000, 2)
    return UniversalResponse(
        status="success",
        data=data,
        meta=UniversalMeta(request_id=req_id, latency_ms=latency, model_provider="parametric_is_cpwd")
    )
