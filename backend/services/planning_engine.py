"""
Parametric planning engine for Construction Project Planning (FR-04).
Implements standard IS / CPWD empirical coefficients and planning algorithms.
"""
from typing import Dict, Any, List

# City cost indices relative to standard baseline (Bengaluru/Delhi/Mumbai tier 1)
CITY_COST_MULTIPLIERS: Dict[str, float] = {
    "Bengaluru": 1.0,
    "Delhi": 1.05,
    "Mumbai": 1.15,
    "Hyderabad": 0.95,
    "Chennai": 1.0,
    "Kolkata": 0.92,
    "Pune": 1.02,
    "Ahmedabad": 0.94,
    "Jaipur": 0.90,
    "Lucknow": 0.88,
    "Default": 1.0,
}

# Grade multipliers and baseline cost per sq.ft (INR)
GRADE_SPECS: Dict[str, Dict[str, Any]] = {
    "standard_residential": {
        "label": "Standard Residential (RCC)",
        "base_cost_per_sqft": 1700.0,
        "cement_coeff": 0.4,       # bags (50kg) per sq.ft
        "steel_coeff": 0.003,      # metric tons per sq.ft
        "sand_coeff": 0.8,         # cu.ft per sq.ft
        "aggregate_coeff": 0.6,    # cu.ft per sq.ft
        "bricks_coeff": 8.0,       # units per sq.ft
        "paint_coeff": 0.18,       # liters per sq.ft
    },
    "premium_residential": {
        "label": "Premium Residential (High-End Finishes)",
        "base_cost_per_sqft": 2400.0,
        "cement_coeff": 0.44,
        "steel_coeff": 0.0035,
        "sand_coeff": 0.85,
        "aggregate_coeff": 0.65,
        "bricks_coeff": 8.0,
        "paint_coeff": 0.22,
    },
    "commercial_rcc": {
        "label": "Commercial RCC Frame",
        "base_cost_per_sqft": 2200.0,
        "cement_coeff": 0.48,
        "steel_coeff": 0.0042,
        "sand_coeff": 0.9,
        "aggregate_coeff": 0.7,
        "bricks_coeff": 6.5,
        "paint_coeff": 0.15,
    },
    "steel_structure": {
        "label": "Pre-Engineered / Structural Steel",
        "base_cost_per_sqft": 2100.0,
        "cement_coeff": 0.25,
        "steel_coeff": 0.0065,
        "sand_coeff": 0.5,
        "aggregate_coeff": 0.4,
        "bricks_coeff": 4.0,
        "paint_coeff": 0.12,
    },
}


def calculate_materials(
    built_up_area_sqft: float,
    floors: int = 1,
    construction_grade: str = "standard_residential"
) -> Dict[str, Any]:
    """
    Computes material takeoff using empirical IS / CPWD coefficients.
    """
    grade = construction_grade if construction_grade in GRADE_SPECS else "standard_residential"
    specs = GRADE_SPECS[grade]

    # Floor density adjustment: slight increase in steel/cement for higher floor load transfers
    floor_factor = 1.0 + (max(0, floors - 1) * 0.02)

    cement_qty = round(built_up_area_sqft * specs["cement_coeff"] * floor_factor, 1)
    steel_qty = round(built_up_area_sqft * specs["steel_coeff"] * floor_factor, 3)
    sand_qty = round(built_up_area_sqft * specs["sand_coeff"], 1)
    aggregate_qty = round(built_up_area_sqft * specs["aggregate_coeff"], 1)
    bricks_qty = round(built_up_area_sqft * specs["bricks_coeff"], 0)
    paint_qty = round(built_up_area_sqft * specs["paint_coeff"], 1)

    materials: List[Dict[str, Any]] = [
        {
            "item": "Cement",
            "quantity": cement_qty,
            "unit": "bags (50kg)",
            "coefficient_per_sqft": specs["cement_coeff"],
        },
        {
            "item": "Structural Steel",
            "quantity": steel_qty,
            "unit": "metric tons",
            "coefficient_per_sqft": specs["steel_coeff"],
        },
        {
            "item": "Fine Aggregate (Sand)",
            "quantity": sand_qty,
            "unit": "cu.ft",
            "coefficient_per_sqft": specs["sand_coeff"],
        },
        {
            "item": "Coarse Aggregate",
            "quantity": aggregate_qty,
            "unit": "cu.ft",
            "coefficient_per_sqft": specs["aggregate_coeff"],
        },
        {
            "item": "Bricks / AAC Blocks",
            "quantity": bricks_qty,
            "unit": "units",
            "coefficient_per_sqft": specs["bricks_coeff"],
        },
        {
            "item": "Paint & Finishes",
            "quantity": paint_qty,
            "unit": "liters",
            "coefficient_per_sqft": specs["paint_coeff"],
        },
    ]

    return {
        "built_up_area_sqft": built_up_area_sqft,
        "floors": floors,
        "construction_grade": grade,
        "materials": materials,
        "calculation_basis": "Empirical IS CPWD norm estimates for RCC framed structures.",
    }


def calculate_cost(
    built_up_area_sqft: float,
    city: str = "Bengaluru",
    construction_grade: str = "standard_residential",
    contingency_percent: float = 7.5,
) -> Dict[str, Any]:
    """
    Computes cost breakdown in INR (₹) across materials, labor, equipment, and contingency.
    """
    grade = construction_grade if construction_grade in GRADE_SPECS else "standard_residential"
    base_rate = GRADE_SPECS[grade]["base_cost_per_sqft"]

    # City multiplier
    multiplier = CITY_COST_MULTIPLIERS.get(city.strip().title(), CITY_COST_MULTIPLIERS["Default"])
    adjusted_rate = base_rate * multiplier

    base_subtotal = built_up_area_sqft * adjusted_rate

    # Standard construction expenditure split:
    # Materials ~ 60%, Labor ~ 30%, Equipment/Machinery ~ 10%
    materials_cost = round(base_subtotal * 0.60, 2)
    labor_cost = round(base_subtotal * 0.28, 2)
    equipment_cost = round(base_subtotal * 0.12, 2)
    subtotal = materials_cost + labor_cost + equipment_cost

    contingency_cost = round(subtotal * (contingency_percent / 100.0), 2)
    total_estimated_cost = round(subtotal + contingency_cost, 2)
    estimated_cost_per_sqft = round(total_estimated_cost / built_up_area_sqft, 2) if built_up_area_sqft > 0 else 0.0

    return {
        "currency": "INR",
        "city": city,
        "construction_grade": grade,
        "materials_cost": materials_cost,
        "labor_cost": labor_cost,
        "equipment_cost": equipment_cost,
        "subtotal": subtotal,
        "contingency_percent": contingency_percent,
        "contingency_cost": contingency_cost,
        "total_estimated_cost": total_estimated_cost,
        "estimated_cost_per_sqft": estimated_cost_per_sqft,
    }


def calculate_schedule(
    built_up_area_sqft: float,
    floors: int = 1,
) -> Dict[str, Any]:
    """
    Generates sequenced project WBS phases with durations, milestones, and dependencies.
    Scales durations smoothly based on area and floor count.
    """
    # Scale factor relative to 3000 sq.ft standard baseline
    area_factor = max(0.6, (built_up_area_sqft / 3000.0) ** 0.5)
    floor_factor = max(1.0, 1.0 + (floors - 1) * 0.35)

    def scale_days(base: int, floor_sensitive: bool = False) -> int:
        multiplier = area_factor * (floor_factor if floor_sensitive else 1.0)
        return max(5, round(base * multiplier))

    d_site = scale_days(12, floor_sensitive=False)
    d_foundation = scale_days(20, floor_sensitive=False)
    d_rcc = scale_days(40, floor_sensitive=True)
    d_masonry = scale_days(35, floor_sensitive=True)
    d_mep = scale_days(45, floor_sensitive=True)
    d_finishing = scale_days(28, floor_sensitive=False)

    phases = [
        {
            "task_id": "T01",
            "name": "Site Clearing & Earthwork Excavation",
            "duration_days": d_site,
            "dependencies": [],
            "milestone": False,
        },
        {
            "task_id": "T02",
            "name": "Foundation & Footing RCC Construction",
            "duration_days": d_foundation,
            "dependencies": ["T01"],
            "milestone": True,
        },
        {
            "task_id": "T03",
            "name": f"RCC Superstructure & Slab Framing ({floors} Floor{'s' if floors > 1 else ''})",
            "duration_days": d_rcc,
            "dependencies": ["T02"],
            "milestone": True,
        },
        {
            "task_id": "T04",
            "name": "Brick Masonry & Internal/External Plastering",
            "duration_days": d_masonry,
            "dependencies": ["T03"],
            "milestone": False,
        },
        {
            "task_id": "T05",
            "name": "MEP (Electrical & Plumbing Rough-in)",
            "duration_days": d_mep,
            "dependencies": ["T04"],
            "milestone": True,
        },
        {
            "task_id": "T06",
            "name": "Flooring, Painting, Fixtures & Final Handover",
            "duration_days": d_finishing,
            "dependencies": ["T05"],
            "milestone": True,
        },
    ]

    total_duration = sum(p["duration_days"] for p in phases)

    return {
        "built_up_area_sqft": built_up_area_sqft,
        "floors": floors,
        "estimated_total_duration_days": total_duration,
        "phases": phases,
    }
