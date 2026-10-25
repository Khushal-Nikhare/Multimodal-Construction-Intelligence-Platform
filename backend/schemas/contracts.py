"""
Schema Definitions & Output Contracts for Platform Modules.
Defines Pydantic models for validation, parsing, normalization, and fallback enforcement
for all features (FR-01 to FR-10) per data-contracts.md.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


# ── Universal Envelope (FR-10) ────────────────────────────────────────────────

class UniversalMeta(BaseModel):
    timestamp: str = Field(...)
    request_id: Optional[str] = None
    latency_ms: Optional[float] = None
    model_provider: Optional[str] = "groq"


class UniversalErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str


class UniversalError(BaseModel):
    code: str
    message: str
    details: Optional[Union[List[UniversalErrorDetail], List[Dict[str, Any]], Any]] = None


class UniversalResponse(BaseModel):
    status: str = "success"  # "success" | "partial" | "error"
    data: Optional[Any] = None
    error: Optional[UniversalError] = None
    meta: Optional[UniversalMeta] = None


# ── FR-01: Safety Monitoring Schema ───────────────────────────────────────────

class HazardItem(BaseModel):
    id: str = Field(default="haz-001")
    category: str = Field(default="OTHER")
    title: str = Field(...)
    severity: str = Field(default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    description: str = Field(...)
    location_hint: Optional[str] = Field(default="Image center")
    corrective_action: str = Field(default="Inspect and remediate per site safety protocol")


class PPESummary(BaseModel):
    compliant_items: List[str] = Field(default_factory=list)
    missing_or_non_compliant: List[str] = Field(default_factory=list)


class SafetyAnalysisData(BaseModel):
    hazards_identified: List[HazardItem] = Field(default_factory=list)
    overall_site_risk: str = Field(default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    ppe_summary: Optional[PPESummary] = None
    uncertainty_note: Optional[str] = Field(default="")
    disclaimer: str = Field(
        default="This analysis is an AI-assisted screening tool and does not replace human safety inspection or constitute formal legal compliance."
    )


# ── FR-02: Structural Crack Analysis Schema ───────────────────────────────────

class CrackFinding(BaseModel):
    crack_type: str = Field(default="HAIRLINE_SURFACE")
    apparent_width_category: str = Field(default="FINE_UNDER_1_MM")
    orientation: str = Field(default="UNSPECIFIED")
    preliminary_severity: str = Field(default="LOW_NON_STRUCTURAL")
    probable_causes: List[str] = Field(default_factory=lambda: ["Thermal shrinkage / drying shrinkage"])
    recommended_inspections: List[str] = Field(default_factory=lambda: ["Periodic visual monitoring"])


class ImageQualityAssessment(BaseModel):
    clarity: str = Field(default="SUFFICIENT")
    lighting: str = Field(default="ADEQUATE")
    recommendation: Optional[str] = Field(default="Maintain calibrated reference marker in future photos.")


class CrackAnalysisData(BaseModel):
    crack_detected: bool = Field(default=False)
    findings: List[CrackFinding] = Field(default_factory=list)
    image_quality_assessment: Optional[ImageQualityAssessment] = None
    disclaimer: str = Field(
        default="AI crack screening is purely indicative and must never be considered a structural engineering diagnosis or fitness-for-use certification."
    )


# ── FR-03: Real Estate Valuation Schema ───────────────────────────────────────

class FactorAdjustment(BaseModel):
    factor: str
    rate_adjustment: float
    rationale: str


class ValuationBand(BaseModel):
    low: float
    high: float
    confidence_level: str = "85%"


class RentalAndROI(BaseModel):
    estimated_monthly_rent: float
    formatted_monthly_rent: str
    estimated_annual_rent: float
    gross_rental_yield_percent: float
    net_roi_percent: float
    projected_5yr_value: float
    formatted_5yr_value: str
    projected_cagr_percent: float


class ValuationData(BaseModel):
    currency: str = "INR"
    estimated_total_value: float
    formatted_total_value: str
    estimated_rate_per_sqft: float
    valuation_band: ValuationBand
    factors_applied: List[FactorAdjustment] = Field(default_factory=list)
    rental_and_roi: Optional[RentalAndROI] = None
    assumptions_and_limitations: str


# ── FR-04: Construction Project Planning Schemas ──────────────────────────────

class MaterialItem(BaseModel):
    item: str
    quantity: float
    unit: str
    coefficient_per_sqft: float


class MaterialsTakeoffData(BaseModel):
    built_up_area_sqft: float
    floors: int = 1
    construction_grade: str = "standard_residential"
    materials: List[MaterialItem]
    calculation_basis: str


class CostBreakdownData(BaseModel):
    currency: str = "INR"
    materials_cost: float
    labor_cost: float
    equipment_cost: float
    subtotal: float
    contingency_cost: float
    total_estimated_cost: float
    estimated_cost_per_sqft: float


class SchedulePhase(BaseModel):
    task_id: str
    name: str
    duration_days: int
    dependencies: List[str] = Field(default_factory=list)
    milestone: bool = False


class TaskScheduleData(BaseModel):
    built_up_area_sqft: float
    floors: int = 1
    estimated_total_duration_days: int
    phases: List[SchedulePhase]


# ── FR-05: Construction Knowledge Assistant Schema ───────────────────────────

class KnowledgeResponseData(BaseModel):
    answer: str
    code_references: List[str] = Field(default_factory=list)
    key_takeaways: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="Educational engineering reference only; project structural specifications take precedence."
    )


# ── FR-06: Construction Chatbot Schema ────────────────────────────────────────

class ChatResponseData(BaseModel):
    session_id: str
    reply: str
    requires_clarification: bool = False
    action_suggestions: List[str] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)


# ── FR-07: Daily Site Assistant Schema ────────────────────────────────────────

class DailyTaskItem(BaseModel):
    task: str
    priority: str = "MEDIUM"
    suggested_crew: int = 0
    execution_notes: str = ""


class DailyResourceItem(BaseModel):
    item: str
    category: str = "MATERIAL_OR_EQUIPMENT"
    purpose: str


class DailySiteAnalysisData(BaseModel):
    activity: str
    labour_count: int
    site_condition: str
    progress_summary: str
    task_breakdown: List[DailyTaskItem] = Field(default_factory=list)
    required_materials_and_equipment: List[DailyResourceItem] = Field(default_factory=list)
    safety_precautions: List[str] = Field(default_factory=list)
    inspection_checklist: List[str] = Field(default_factory=list)
    identified_delays: List[str] = Field(default_factory=list)
    operational_risks: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="AI-assisted daily coordination guidance only. The site engineer and approved method statements govern execution and safety decisions."
    )


# ── FR-08: Weather-Aware Advisory Schema ──────────────────────────────────────

class WeatherObservationData(BaseModel):
    city: str
    observed_at: str
    temperature_c: float
    relative_humidity_percent: float
    wind_speed_kmh: float
    precipitation_mm: float
    precipitation_probability_percent: int
    weather_code: int
    source: str


class WeatherAdvisoryData(BaseModel):
    activity: str
    recommendation: str
    recommendation_reason: str
    weather: WeatherObservationData
    weather_related_risks: List[str] = Field(default_factory=list)
    safety_precautions: List[str] = Field(default_factory=list)
    mitigation_steps: List[str] = Field(default_factory=list)
    data_freshness_note: str
    disclaimer: str = Field(
        default="This is an operational advisory based on the stated forecast window. The responsible site engineer must verify site conditions, equipment limits, and approved procedures before work proceeds."
    )
