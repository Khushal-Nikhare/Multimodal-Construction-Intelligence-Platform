"""
Valuation engine for Real Estate Valuation (FR-03).
Implements realistic Indian market benchmark tables across major cities and localities,
with parametric adjustments for floor rise, amenities, property age, and conditions.
Calculates ROI, gross rental yields, and appreciation outlooks.
"""
from typing import Dict, Any, List, Optional, Tuple

# Baseline rates per sq.ft for indexed city localities (INR ₹)
LOCALITY_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "bengaluru": {
        "whitefield": 7600.0,
        "indiranagar": 15500.0,
        "koramangala": 14000.0,
        "bellandur": 9200.0,
        "electronic city": 5200.0,
        "hebbal": 9800.0,
        "marathahalli": 7200.0,
        "sarjapur road": 7800.0,
        "default": 8000.0,
    },
    "mumbai": {
        "bandra west": 48000.0,
        "andheri west": 24000.0,
        "andheri east": 18500.0,
        "powai": 22000.0,
        "worli": 45000.0,
        "thane": 12500.0,
        "navi mumbai": 11000.0,
        "default": 20000.0,
    },
    "delhi": {
        "south delhi": 22000.0,
        "dwarka": 9500.0,
        "rohini": 8500.0,
        "vasant kunj": 19000.0,
        "noida central": 7500.0,
        "greater noida": 4800.0,
        "gurugram cyber city": 16000.0,
        "gurugram golf course": 25000.0,
        "default": 11000.0,
    },
    "hyderabad": {
        "gachibowli": 8800.0,
        "hitec city": 9500.0,
        "madhapur": 10200.0,
        "kondapur": 8200.0,
        "jubilee hills": 19500.0,
        "banjara hills": 18500.0,
        "default": 7500.0,
    },
    "chennai": {
        "omr": 6200.0,
        "velachery": 7800.0,
        "anna nagar": 14000.0,
        "t nagar": 15500.0,
        "adyar": 16500.0,
        "default": 7500.0,
    },
    "pune": {
        "hinjewadi": 6400.0,
        "wakad": 7200.0,
        "baner": 8800.0,
        "kalyani nagar": 12500.0,
        "koregaon park": 14500.0,
        "default": 7000.0,
    },
    "kolkata": {
        "salt lake": 7800.0,
        "new town": 5800.0,
        "ballygunge": 14000.0,
        "alipore": 16000.0,
        "default": 6500.0,
    },
}

PROPERTY_TYPE_MULTIPLIERS: Dict[str, float] = {
    "residential_apartment": 1.0,
    "independent_house": 1.15,
    "villa": 1.25,
    "commercial_office": 1.35,
    "commercial_retail": 1.55,
    "plot_land": 0.85,
}

AMENITY_VALUES: Dict[str, Tuple[float, str]] = {
    "covered_parking": (150.0, "Dedicated covered car parking spot"),
    "clubhouse": (100.0, "Access to community clubhouse and fitness center"),
    "power_backup": (100.0, "100% DG power backup system"),
    "swimming_pool": (100.0, "Maintained swimming pool facility"),
    "security_24x7": (75.0, "CCTV and 24/7 security guard coverage"),
    "lift": (75.0, "High-speed passenger elevator"),
    "piped_gas": (50.0, "Piped natural gas connection"),
    "solar_panels": (50.0, "Rooftop solar water/power installation"),
}


def format_inr_crore_lakh(amount: float) -> str:
    """Format large INR numbers into readable Lakh / Crore format."""
    if amount >= 10000000:
        val = amount / 10000000.0
        return f"₹{val:.2f} Crore"
    elif amount >= 100000:
        val = amount / 100000.0
        return f"₹{val:.2f} Lakh"
    else:
        return f"₹{amount:,.0f}"


def calculate_valuation(
    city: str,
    locality: str,
    property_type: str,
    built_up_area_sqft: float,
    age_years: int = 0,
    condition: str = "good",
    floor_number: int = 1,
    total_floors: int = 1,
    amenities: Optional[List[str]] = None,
    carpet_area_sqft: Optional[float] = None,
    pincode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Computes property valuation, rate per sq.ft, valuation band, itemized factors,
    rental income potential, and ROI estimation.
    """
    amenities = amenities or []
    city_key = (city or "").strip().lower()
    locality_key = (locality or "").strip().lower()

    # Locality lookup
    city_data = LOCALITY_BENCHMARKS.get(city_key)
    unrecognized_locality = False

    if city_data:
        if locality_key in city_data:
            base_rate = city_data[locality_key]
            locality_rationale = f"Prevailing {locality.title()} secondary market benchmark"
        else:
            base_rate = city_data.get("default", 7500.0)
            unrecognized_locality = True
            locality_rationale = f"District baseline for {city.title()} (locality '{locality}' unindexed, applied wider variance)"
    else:
        base_rate = 6500.0
        unrecognized_locality = True
        locality_rationale = f"General urban Tier-2/3 baseline (city '{city}' unindexed, applied wider variance)"

    # Property type multiplier
    type_mult = PROPERTY_TYPE_MULTIPLIERS.get(property_type, 1.0)
    adjusted_base_rate = round(base_rate * type_mult, 2)

    factors_applied: List[Dict[str, Any]] = [
        {
            "factor": "Locality Baseline",
            "rate_adjustment": adjusted_base_rate,
            "rationale": locality_rationale,
        }
    ]

    current_rate = adjusted_base_rate

    # Floor rise premium (for apartments above 4th floor)
    if property_type == "residential_apartment" and floor_number > 4:
        floor_premium = min(500.0, round((floor_number - 4) * 50.0, 2))
        current_rate += floor_premium
        factors_applied.append({
            "factor": "Floor Rise Premium",
            "rate_adjustment": floor_premium,
            "rationale": f"{floor_number}th floor in a {total_floors}-storey structure",
        })

    # Amenity package
    amenity_total = 0.0
    verified_amenities = []
    for am in amenities:
        clean_am = am.strip().lower()
        if clean_am in AMENITY_VALUES:
            val, desc = AMENITY_VALUES[clean_am]
            amenity_total += val
            verified_amenities.append(desc)
    
    if amenity_total > 0:
        current_rate += amenity_total
        factors_applied.append({
            "factor": "Amenity Package",
            "rate_adjustment": round(amenity_total, 2),
            "rationale": f"Verified {len(verified_amenities)} premium amenities",
        })

    # Age depreciation (straight line 1.25% per year up to 35%)
    if age_years > 0:
        depreciation_pct = min(0.35, age_years * 0.0125)
        # Apply depreciation to the structural portion of rate
        depreciation_rate = -round(current_rate * depreciation_pct, 2)
        current_rate += depreciation_rate
        factors_applied.append({
            "factor": "Age Depreciation",
            "rate_adjustment": depreciation_rate,
            "rationale": f"Straight-line building depreciation over {age_years} year{'s' if age_years > 1 else ''}",
        })

    # Condition adjustment
    condition_clean = (condition or "good").strip().lower()
    if condition_clean == "excellent":
        cond_adj = round(current_rate * 0.05, 2)
        current_rate += cond_adj
        factors_applied.append({
            "factor": "Condition Premium",
            "rate_adjustment": cond_adj,
            "rationale": "Superior maintenance and pristine structural condition",
        })
    elif condition_clean == "needs_renovation" or condition_clean == "poor":
        cond_adj = -round(current_rate * 0.10, 2)
        current_rate += cond_adj
        factors_applied.append({
            "factor": "Condition Discount",
            "rate_adjustment": cond_adj,
            "rationale": "Visible wear or pending civil/finishing maintenance",
        })

    # Final rate per sq.ft
    estimated_rate_per_sqft = max(1000.0, round(current_rate, 2))
    estimated_total_value = round(estimated_rate_per_sqft * built_up_area_sqft, 2)

    # Valuation Band
    variance_pct = 0.12 if unrecognized_locality else 0.0625
    low_band = round(estimated_total_value * (1.0 - variance_pct), 2)
    high_band = round(estimated_total_value * (1.0 + variance_pct), 2)
    confidence = "70%" if unrecognized_locality else "85%"

    # Rental & ROI calculations
    # Typical Indian residential gross rental yield: ~2.8% to 3.5%; commercial ~6.5% to 8.5%
    is_commercial = "commercial" in property_type
    gross_yield_pct = 7.2 if is_commercial else 3.1
    annual_rental_income = round(estimated_total_value * (gross_yield_pct / 100.0), 2)
    monthly_rental_income = round(annual_rental_income / 12.0, 2)

    # Maintenance & taxes deduction (~15% of rental)
    net_annual_rental = round(annual_rental_income * 0.85, 2)
    net_roi_percent = round((net_annual_rental / estimated_total_value) * 100.0, 2)

    # Appreciation outlook (typical 5-year CAGR in major metros ~ 5.5% - 8.5%)
    appreciation_cagr_pct = 6.8 if not unrecognized_locality else 5.2
    five_year_projected_value = round(estimated_total_value * ((1 + appreciation_cagr_pct / 100.0) ** 5), 2)

    # Assumptions & Limitations
    limitations = (
        "Estimate based on parametric locality benchmarks without interior inspection or title-deed legal validation."
    )
    if unrecognized_locality:
        limitations += f" Note: Locality '{locality}' was not found in high-granularity indices; city baseline with wider margin applied."

    return {
        "currency": "INR",
        "estimated_total_value": estimated_total_value,
        "formatted_total_value": format_inr_crore_lakh(estimated_total_value),
        "estimated_rate_per_sqft": estimated_rate_per_sqft,
        "valuation_band": {
            "low": low_band,
            "high": high_band,
            "confidence_level": confidence,
        },
        "factors_applied": factors_applied,
        "rental_and_roi": {
            "estimated_monthly_rent": monthly_rental_income,
            "formatted_monthly_rent": f"₹{monthly_rental_income:,.0f}/mo",
            "estimated_annual_rent": annual_rental_income,
            "gross_rental_yield_percent": gross_yield_pct,
            "net_roi_percent": net_roi_percent,
            "projected_5yr_value": five_year_projected_value,
            "formatted_5yr_value": format_inr_crore_lakh(five_year_projected_value),
            "projected_cagr_percent": appreciation_cagr_pct,
        },
        "assumptions_and_limitations": limitations,
    }
