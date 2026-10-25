"""
FR-03 – Real Estate Valuation Router
Endpoints:
  - POST /api/valuation/estimate (Structured JSON Request per Contract 3.3)
  - POST /api/real-estate-valuation (Alias / Form-data compatible endpoint per Activity 3.2)
"""
import logging
import time
import uuid
from typing import Optional, List, Dict, Any, Union

from fastapi import APIRouter, Form, HTTPException, status
from pydantic import BaseModel, Field

from schemas.response import UniversalError, UniversalMeta, UniversalResponse
from services.valuation_engine import calculate_valuation, LOCALITY_BENCHMARKS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["FR-03: Real Estate Valuation"])


# ── Nested Models for Contract 3.3 ────────────────────────────────────────────

class LocationModel(BaseModel):
    city: str = Field(..., description="City name (e.g. Bengaluru, Mumbai, Delhi)")
    locality: str = Field(..., description="Locality or sub-market name (e.g. Whitefield)")
    pincode: Optional[str] = Field(None, description="6-digit postal code")


class ValuationEstimateRequest(BaseModel):
    location: LocationModel
    property_type: str = Field("residential_apartment", description="Property category")
    built_up_area_sqft: float = Field(..., gt=0.0, description="Built-up area in square feet (must be > 0)")
    carpet_area_sqft: Optional[float] = Field(None, gt=0.0, description="Usable carpet area in square feet")
    age_years: int = Field(0, ge=0, le=100, description="Age of structure in years")
    condition: Optional[str] = Field("good", description="Property physical condition")
    floor_number: int = Field(1, ge=0, le=120, description="Floor level of property unit")
    total_floors: int = Field(1, ge=1, le=120, description="Total building floors")
    amenities: Optional[List[str]] = Field(default_factory=list, description="List of amenities")


# ── Core Handlers ─────────────────────────────────────────────────────────────

def _process_valuation(
    city: str,
    locality: str,
    built_up_area_sqft: float,
    property_type: str = "residential_apartment",
    age_years: int = 0,
    condition: str = "good",
    floor_number: int = 1,
    total_floors: int = 1,
    amenities: Optional[List[str]] = None,
    carpet_area_sqft: Optional[float] = None,
    pincode: Optional[str] = None,
) -> Dict[str, Any]:
    # Scenario 3.2 Validation
    if built_up_area_sqft <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "error": {
                    "code": "INVALID_AREA",
                    "message": "built_up_area_sqft must be strictly greater than 0.",
                }
            }
        )

    return calculate_valuation(
        city=city,
        locality=locality,
        property_type=property_type,
        built_up_area_sqft=built_up_area_sqft,
        age_years=age_years,
        condition=condition,
        floor_number=floor_number,
        total_floors=total_floors,
        amenities=amenities,
        carpet_area_sqft=carpet_area_sqft,
        pincode=pincode,
    )


# ── Primary Contract Endpoint ─────────────────────────────────────────────────

@router.post("/api/valuation/estimate", response_model=UniversalResponse)
async def estimate_valuation_json(payload: ValuationEstimateRequest):
    """
    Standard Data Contract 3.3 endpoint accepting JSON body.
    """
    t0 = time.time()
    req_id = f"req-val-{uuid.uuid4().hex[:8]}"

    data = _process_valuation(
        city=payload.location.city,
        locality=payload.location.locality,
        built_up_area_sqft=payload.built_up_area_sqft,
        property_type=payload.property_type,
        age_years=payload.age_years,
        condition=payload.condition or "good",
        floor_number=payload.floor_number,
        total_floors=payload.total_floors,
        amenities=payload.amenities,
        carpet_area_sqft=payload.carpet_area_sqft,
        pincode=payload.location.pincode,
    )

    latency = round((time.time() - t0) * 1000, 2)
    return UniversalResponse(
        status="success",
        data=data,
        meta=UniversalMeta(request_id=req_id, latency_ms=latency, model_provider="parametric_real_estate")
    )


# ── Activity 3.2 Form-Data / Alias Endpoint ───────────────────────────────────

@router.post("/api/real-estate-valuation", response_model=UniversalResponse)
async def estimate_valuation_form(
    city: str = Form(...),
    locality: str = Form(...),
    built_up_area_sqft: float = Form(...),
    property_type: str = Form("residential_apartment"),
    age_years: int = Form(0),
    condition: str = Form("good"),
    floor_number: int = Form(1),
    total_floors: int = Form(1),
    amenities: Optional[str] = Form(None), # comma-separated string from FormData
    pincode: Optional[str] = Form(None),
):
    """
    Activity 3.2 endpoint accepting browser FormData submissions via Axios.
    """
    t0 = time.time()
    req_id = f"req-val-{uuid.uuid4().hex[:8]}"

    amenity_list = [a.strip() for a in amenities.split(",")] if amenities else []

    data = _process_valuation(
        city=city,
        locality=locality,
        built_up_area_sqft=built_up_area_sqft,
        property_type=property_type,
        age_years=age_years,
        condition=condition,
        floor_number=floor_number,
        total_floors=total_floors,
        amenities=amenity_list,
        pincode=pincode,
    )

    latency = round((time.time() - t0) * 1000, 2)
    return UniversalResponse(
        status="success",
        data=data,
        meta=UniversalMeta(request_id=req_id, latency_ms=latency, model_provider="parametric_real_estate")
    )
