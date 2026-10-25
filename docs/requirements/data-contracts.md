# Data Contracts and API Specifications
## AI-Powered Multimodal Construction Intelligence Platform

**Document Version:** 1.0.0  
**Status:** Approved for Baseline Design  
**Date:** 2026-10-25  
**Workspace:** `f:/BTech-CS-DS/vibe`  

---

## 1. Universal Response Envelope

All API endpoints must return payloads wrapped in this standard structure:

### Standard Success Response Format
```json
{
  "status": "success",
  "data": {},
  "error": null,
  "meta": {
    "timestamp": "2026-10-25T12:00:00Z",
    "request_id": "req-98f3b2e1",
    "latency_ms": 412,
    "model_provider": "gemini-1.5-pro"
  }
}
```

### Standard Error Response Format
```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "INVALID_IMAGE_PAYLOAD",
    "message": "Uploaded file exceeds maximum permissible size of 10 MB.",
    "details": [
      {
        "field": "image",
        "issue": "File size 14,204,112 bytes > 10,485,760 bytes"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-10-25T12:00:00Z",
    "request_id": "req-98f3b2e2",
    "latency_ms": 15
  }
}
```

---

## 2. Feature Input and Output Matrix

| Feature | Endpoint | HTTP Method | Content-Type | Inputs (Required & Optional) | Expected Output Payload |
|---|---|---|---|---|---|
| **Safety Monitoring** | `/api/safety/analyze` | `POST` | `multipart/form-data` | `image` (Required, binary)<br>`location` (Optional, string)<br>`description` (Optional, string) | List of PPE & environmental hazards, severity ratings, bounding boxes, recommendations, uncertainty notes, disclaimer. |
| **Crack Detection** | `/api/cracks/analyze` | `POST` | `multipart/form-data` | `image` (Required, binary)<br>`surface_type` (Optional, enum)<br>`structural_element` (Optional, string) | Detected crack types, preliminary severity, estimated causes, inspection recommendations, disclaimer. |
| **Valuation** | `/api/valuation/estimate` | `POST` | `application/json` | `location` (Req, object)<br>`property_type` (Req, enum)<br>`built_up_area_sqft` (Req, float)<br>`age_years` (Req, int)<br>`condition` (Req, enum)<br>`amenities` (Opt, list) | Estimated value in ₹, rate per sq.ft in ₹, low-high valuation range, factor breakdowns, assumptions. |
| **Planning: Materials** | `/api/planning/materials` | `POST` | `application/json` | `built_up_area_sqft` (Req, float)<br>`floors` (Req, int)<br>`construction_grade` (Req, enum)<br>`custom_rates` (Opt, object) | Quantities for Cement, Steel, Sand, Aggregate, Bricks, Paints with units and formulas. |
| **Planning: Cost** | `/api/planning/cost` | `POST` | `application/json` | `materials_summary` (Req, object)<br>`location_city` (Req, string)<br>`contingency_percentage` (Opt, float) | Itemized material costs in ₹, labor costs in ₹, equipment costs, contingency, total estimated project cost. |
| **Planning: Schedule** | `/api/planning/schedule` | `POST` | `application/json` | `built_up_area_sqft` (Req, float)<br>`floors` (Req, int)<br>`crew_size` (Opt, int) | Ordered task list, durations (days), dependencies, milestones, critical path flag. |
| **Knowledge Assistant** | `/api/knowledge/ask` | `POST` | `application/json` | `query` (Req, string)<br>`domain_context` (Opt, string)<br>`reference_standards` (Opt, list) | Explanation, code references (e.g., IS 456), procedural steps, limitations disclaimer. |
| **Construction Chatbot** | `/api/chat` | `POST` | `application/json` | `message` (Req, string)<br>`session_id` (Opt, string)<br>`conversation_history` (Opt, list) | Assistant reply, clarifying questions (if ambiguous), session_id, safety guardrails. |
| **Daily Site Assistant** | `/api/site-assistant/analyze` | `POST` | `application/json` | `site_date` (Req, string)<br>`work_completed` (Req, string)<br>`delays_or_issues` (Opt, string)<br>`workforce_count` (Opt, int) | Synthesized progress summary, delayed activities, risk analysis, actionable coordination advice. |
| **Weather Advisory** | `/api/weather/advisory` | `GET` | `query-params` | `city` (Req, string)<br>`activity` (Opt, string) | Current weather metrics, forecast window, construction activity risks, actionable precautions, timestamp. |

---

## 3. Detailed Request and Response Schemas

### 3.1 FR-01: Safety Monitoring (`POST /api/safety/analyze`)

**Request (Multipart Form Data):**
* `image`: Binary file (`image/jpeg`, `image/png`, `image/webp`, max 10MB)
* `location`: Text string (e.g., `"Tower B, 4th Floor Slab"`)
* `description`: Text string (e.g., `"Workers preparing rebar cages near perimeter"`)

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "hazards_identified": [
      {
        "id": "haz-001",
        "category": "PPE_NON_COMPLIANCE",
        "title": "Missing Hard Hat",
        "severity": "HIGH",
        "description": "Worker near western edge observed without safety helmet.",
        "location_hint": "Center-left foreground",
        "corrective_action": "Issue immediate stop-work instruction until helmet is worn and inspected."
      },
      {
        "id": "haz-002",
        "category": "FALL_HAZARD",
        "title": "Unprotected Slab Edge",
        "severity": "CRITICAL",
        "description": "Perimeter slab edge lacks standard toe-boards and guardrail barriers.",
        "location_hint": "Far right perimeter",
        "corrective_action": "Install temporary OSHA-compliant edge protection netting and guardrails."
      }
    ],
    "overall_site_risk": "HIGH",
    "uncertainty_note": "Partial shadow in the rear right quadrant prevents full verification of footwear.",
    "disclaimer": "This analysis is an AI-assisted screening tool and does not replace human safety inspection or constitute formal legal compliance."
  },
  "error": null,
  "meta": {
    "timestamp": "2026-10-25T12:02:10Z",
    "request_id": "req-safe-101",
    "latency_ms": 2840,
    "model_provider": "gemini-1.5-pro"
  }
}
```

---

### 3.2 FR-02: Structural Crack Analysis (`POST /api/cracks/analyze`)

**Request (Multipart Form Data):**
* `image`: Binary file (max 10MB)
* `surface_type`: String (`concrete`, `brick_masonry`, `plaster`, `stone`)
* `structural_element`: String (`beam`, `column`, `shear_wall`, `slab`, `non_structural_wall`)

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "crack_detected": true,
    "findings": [
      {
        "crack_type": "DIAGONAL_SHEAR",
        "apparent_width_category": "MEDIUM_1_TO_3_MM",
        "orientation": "DIAGONAL_45_DEGREE",
        "preliminary_severity": "MODERATE_STRUCTURAL",
        "probable_causes": [
          "Differential foundation settlement",
          "Excessive shear stress near support junction"
        ],
        "recommended_inspections": [
          "Install glass/tell-tale crack monitors to check active propagation over 14 days",
          "Engage a licensed Structural Engineer for core or rebound hammer evaluation"
        ]
      }
    ],
    "image_quality_assessment": {
      "clarity": "SUFFICIENT",
      "lighting": "ADEQUATE",
      "recommendation": "Maintain calibrated scale marker (ruler/coin) in future photos for precise millimeter measurement."
    },
    "disclaimer": "AI crack screening is purely indicative and must never be considered a structural engineering diagnosis or fitness-for-use certification."
  },
  "error": null,
  "meta": {
    "timestamp": "2026-10-25T12:03:00Z",
    "request_id": "req-crk-202",
    "latency_ms": 3110
  }
}
```

---

### 3.3 FR-03: Real Estate Valuation (`POST /api/valuation/estimate`)

**Request Payload:**
```json
{
  "location": {
    "city": "Bengaluru",
    "locality": "Whitefield",
    "pincode": "560066"
  },
  "property_type": "residential_apartment",
  "built_up_area_sqft": 1450.0,
  "carpet_area_sqft": 1180.0,
  "age_years": 4,
  "condition": "good",
  "floor_number": 6,
  "total_floors": 14,
  "amenities": ["covered_parking", "clubhouse", "power_backup", "swimming_pool"]
}
```

**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "currency": "INR",
    "estimated_total_value": 11600000.0,
    "formatted_total_value": "₹1.16 Crore",
    "estimated_rate_per_sqft": 8000.0,
    "valuation_band": {
      "low": 10875000.0,
      "high": 12325000.0,
      "confidence_level": "85%"
    },
    "factors_applied": [
      {
        "factor": "Locality Baseline",
        "rate_adjustment": 7600.0,
        "rationale": "Prevailing Whitefield secondary market benchmark"
      },
      {
        "factor": "Floor Rise Premium",
        "rate_adjustment": 150.0,
        "rationale": "6th floor in high-rise structure"
      },
      {
        "factor": "Amenity Package",
        "rate_adjustment": 450.0,
        "rationale": "Gated society amenities verified"
      },
      {
        "factor": "Age Depreciation",
        "rate_adjustment": -200.0,
        "rationale": "Straight-line building depreciation over 4 years"
      }
    ],
    "assumptions_and_limitations": "Estimate based on parametric locality benchmarks without interior inspection or title-deed legal validation."
  },
  "error": null,
  "meta": {
    "timestamp": "2026-10-25T12:04:15Z",
    "request_id": "req-val-303",
    "latency_ms": 120
  }
}
```

---

### 3.4 FR-04: Project Planning (`POST /api/planning/materials`, `POST /api/planning/cost`, `POST /api/planning/schedule`)

#### A. Material Takeoff Request (`/api/planning/materials`)
```json
{
  "built_up_area_sqft": 3000.0,
  "floors": 2,
  "construction_grade": "standard_residential"
}
```
**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "built_up_area_sqft": 3000.0,
    "materials": [
      {
        "item": "Cement",
        "quantity": 1200.0,
        "unit": "bags (50kg)",
        "coefficient_per_sqft": 0.4
      },
      {
        "item": "Structural Steel",
        "quantity": 9.0,
        "unit": "metric tons",
        "coefficient_per_sqft": 0.003
      },
      {
        "item": "Fine Aggregate (Sand)",
        "quantity": 2400.0,
        "unit": "cu.ft",
        "coefficient_per_sqft": 0.8
      },
      {
        "item": "Coarse Aggregate",
        "quantity": 1800.0,
        "unit": "cu.ft",
        "coefficient_per_sqft": 0.6
      },
      {
        "item": "Bricks / AAC Blocks",
        "quantity": 24000.0,
        "unit": "units",
        "coefficient_per_sqft": 8.0
      }
    ],
    "calculation_basis": "Empirical IS CPWD norm estimates for RCC framed residential structures."
  },
  "error": null,
  "meta": { "timestamp": "2026-10-25T12:05:00Z", "latency_ms": 85 }
}
```

#### B. Cost Breakdown Request (`/api/planning/cost`)
```json
{
  "built_up_area_sqft": 3000.0,
  "city": "Bengaluru",
  "contingency_percent": 7.5
}
```
**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "currency": "INR",
    "materials_cost": 3150000.0,
    "labor_cost": 1500000.0,
    "equipment_cost": 450000.0,
    "subtotal": 5100000.0,
    "contingency_cost": 382500.0,
    "total_estimated_cost": 5482500.0,
    "estimated_cost_per_sqft": 1827.5
  },
  "error": null,
  "meta": { "timestamp": "2026-10-25T12:05:20Z", "latency_ms": 64 }
}
```

#### C. Task Schedule Request (`/api/planning/schedule`)
```json
{
  "built_up_area_sqft": 3000.0,
  "floors": 2
}
```
**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "estimated_total_duration_days": 180,
    "phases": [
      {
        "task_id": "T01",
        "name": "Site Clearing & Excavation",
        "duration_days": 12,
        "dependencies": [],
        "milestone": false
      },
      {
        "task_id": "T02",
        "name": "Foundation & Footing RCC",
        "duration_days": 20,
        "dependencies": ["T01"],
        "milestone": true
      },
      {
        "task_id": "T03",
        "name": "Ground & First Floor RCC Frame",
        "duration_days": 40,
        "dependencies": ["T02"],
        "milestone": true
      },
      {
        "task_id": "T04",
        "name": "Brick Masonry & Plastering",
        "duration_days": 35,
        "dependencies": ["T03"],
        "milestone": false
      },
      {
        "task_id": "T05",
        "name": "MEP & Finishing Works",
        "duration_days": 45,
        "dependencies": ["T04"],
        "milestone": true
      }
    ]
  },
  "error": null,
  "meta": { "timestamp": "2026-10-25T12:05:40Z", "latency_ms": 78 }
}
```

---

### 3.5 FR-05: Construction Knowledge Assistant (`POST /api/knowledge/ask`)

**Request Payload:**
```json
{
  "query": "What is the minimum curing period for OPC concrete according to IS 456?",
  "reference_standard": "IS 456:2000"
}
```
**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "answer": "According to IS 456:2000 (Clause 13.5), concrete using Ordinary Portland Cement (OPC) must be cured for at least 7 days under normal weather conditions. In hot, dry weather or when using mineral admixtures (fly ash/slag), the curing period should be extended to at least 10 to 14 days.",
    "code_references": ["IS 456:2000 Clause 13.5", "SP 23 Concrete Handbook"],
    "key_takeaways": [
      "Minimum 7 days continuous wet curing for OPC in normal humidity.",
      "Minimum 10 days for blended cements or dry/hot environments.",
      "Adequate curing achieves compressive strength and durability."
    ],
    "disclaimer": "Educational engineering reference only; project structural specifications take precedence."
  },
  "error": null,
  "meta": { "timestamp": "2026-10-25T12:06:10Z", "latency_ms": 1420 }
}
```

---

### 3.6 FR-06: Construction Chatbot (`POST /api/chat`)

**Request Payload:**
```json
{
  "session_id": "sess-alpha-789",
  "message": "Can I remove the props from a 4m RCC slab after 5 days?",
  "history": [
    { "role": "user", "content": "We cast a 4-meter residential floor slab on Monday." }
  ]
}
```
**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "session_id": "sess-alpha-789",
    "reply": "No, removing props after only 5 days is hazardous and violates standard guidelines. Under IS 456:2000 (Table 5), props supporting slabs spanning up to 4.5 meters must remain in place for at least 7 days, and longer if temperature is below 15°C or blended cements were used. Premature stripping may lead to excessive deflection, cracking, or catastrophic collapse.",
    "requires_clarification": false,
    "suggested_followups": [
      "What is the minimum cube compressive strength required prior to formwork stripping?",
      "How do ambient temperature variations influence formwork removal timing?"
    ]
  },
  "error": null,
  "meta": { "timestamp": "2026-10-25T12:06:50Z", "latency_ms": 1650 }
}
```

---

### 3.7 FR-07: Daily Site Assistant (`POST /api/site-assistant/analyze`)

**Request Payload:**
```json
{
  "site_date": "2026-10-25",
  "work_completed": "Completed column reinforcement for Grid A1-A4. 12 masons on site.",
  "delays_or_issues": "Ready-mix concrete truck delayed by 3 hours due to traffic; pour rescheduled to 4 PM.",
  "workforce_count": 18
}
```
**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "progress_summary": "Rebar detailing for Grid A1-A4 completed with 18 personnel active.",
    "identified_delays": [
      "3-hour delay in RMC delivery forced shifting of pour schedule to late afternoon."
    ],
    "operational_risks": [
      "Pouring in late afternoon increases risk of lighting deficits and night curing supervision challenges.",
      "Potential initial setting time risk if truck transit time was extended."
    ],
    "recommended_actions": [
      "Conduct slump test and temperature check on arriving RMC before pour authorization.",
      "Deploy portable task lighting rigs around Grid A1-A4.",
      "Ensure curing team is scheduled for next morning shift."
    ]
  },
  "error": null,
  "meta": { "timestamp": "2026-10-25T12:07:30Z", "latency_ms": 1380 }
}
```

---

### 3.8 FR-08: Weather-Aware Advisory (`GET /api/weather/advisory?city=Bengaluru&activity=concreting`)

**Response Payload:**
```json
{
  "status": "success",
  "data": {
    "location": "Bengaluru, Karnataka",
    "forecast_timestamp": "2026-10-25T12:00:00Z",
    "source": "Open-Meteo / Configured Weather Service",
    "current_conditions": {
      "temperature_celsius": 29.5,
      "relative_humidity_percent": 78,
      "precipitation_probability": 65,
      "wind_speed_kmh": 14.0,
      "condition_summary": "Scattered afternoon thunderstorms"
    },
    "activity_advisory": {
      "target_activity": "concreting",
      "risk_level": "WARNING",
      "recommended_precautions": [
        "High rain probability (65%) poses wash-out risk on fresh slab surfaces.",
        "Keep heavy-gauge polythene tarpaulins ready on site before casting commences.",
        "Avoid adding unmeasured site water to counteract temperature; utilize superplasticizers if required."
      ]
    }
  },
  "error": null,
  "meta": { "timestamp": "2026-10-25T12:08:10Z", "latency_ms": 190 }
}
```
