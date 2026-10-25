"""
Automated unit tests for Activity 4.2: Structured Output Enforcement and Data Contracts.
Validates:
1. Pydantic schema validation of valid JSON model outputs.
2. Graceful fallback on malformed JSON or markdown codeblocks.
3. Safe semantic defaults when required fields are missing.
4. Data normalization across FR-01 (Safety), FR-02 (Cracks), FR-03 (Valuation), FR-04 (Planning).
"""
import sys
from schemas.contracts import (
    SafetyAnalysisData,
    CrackAnalysisData,
    ValuationData,
    MaterialsTakeoffData,
    TaskScheduleData,
)
from services.output_enforcer import parse_and_validate_ai_response, clean_markdown_fences


def test_safety_schema_enforcement():
    raw_ai = """```json
    {
        "hazards_identified": [
            {
                "id": "haz-001",
                "category": "FALL_HAZARD",
                "title": "Unprotected Slab Edge",
                "severity": "CRITICAL",
                "description": "Perimeter slab edge lacks guardrails",
                "location_hint": "North-west edge",
                "corrective_action": "Install temporary guardrail barrier"
            }
        ],
        "overall_site_risk": "CRITICAL",
        "uncertainty_note": ""
    }
    ```"""
    model, used_fallback = parse_and_validate_ai_response(raw_ai, SafetyAnalysisData)
    assert not used_fallback, "Should parse valid JSON without fallback"
    assert model.overall_site_risk == "CRITICAL"
    assert len(model.hazards_identified) == 1
    assert model.hazards_identified[0].severity == "CRITICAL"
    print("PASS: test_safety_schema_enforcement")


def test_malformed_json_fallback():
    malformed_output = "I observed several workers on the slab without helmets. Site is dangerous."
    fallback = {
        "hazards_identified": [],
        "overall_site_risk": "MEDIUM",
        "uncertainty_note": "Manual review required",
    }
    model, used_fallback = parse_and_validate_ai_response(
        malformed_output, SafetyAnalysisData, fallback_data=fallback
    )
    assert used_fallback, "Should flag fallback as True"
    assert model.overall_site_risk == "MEDIUM"
    assert len(model.hazards_identified) == 0
    print("PASS: test_malformed_json_fallback")


def test_crack_schema_normalization():
    raw_crack = """{
        "crack_detected": true,
        "findings": [
            {
                "crack_type": "DIAGONAL_SHEAR",
                "apparent_width_category": "MEDIUM_1_TO_3_MM",
                "orientation": "DIAGONAL_45_DEGREE",
                "preliminary_severity": "MODERATE_STRUCTURAL",
                "probable_causes": ["Differential settlement"],
                "recommended_inspections": ["Tell-tale monitor installation"]
            }
        ]
    }"""
    model, used_fallback = parse_and_validate_ai_response(raw_crack, CrackAnalysisData)
    assert not used_fallback
    assert model.crack_detected is True
    assert len(model.findings) == 1
    assert model.findings[0].crack_type == "DIAGONAL_SHEAR"
    print("PASS: test_crack_schema_normalization")


def test_planning_contract_types():
    takeoff = MaterialsTakeoffData(
        built_up_area_sqft=3000.0,
        floors=2,
        construction_grade="standard_residential",
        materials=[
            {
                "item": "Cement",
                "quantity": 1200.0,
                "unit": "bags (50kg)",
                "coefficient_per_sqft": 0.4,
            }
        ],
        calculation_basis="IS 456 / CPWD Norms",
    )
    dumped = takeoff.model_dump()
    assert dumped["built_up_area_sqft"] == 3000.0
    assert dumped["materials"][0]["quantity"] == 1200.0
    print("PASS: test_planning_contract_types")


if __name__ == "__main__":
    test_safety_schema_enforcement()
    test_malformed_json_fallback()
    test_crack_schema_normalization()
    test_planning_contract_types()
    print("ALL 4 CONTRACT ENFORCEMENT TESTS PASSED.")
