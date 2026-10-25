# Functional Requirements Specification (FRS)
## AI-Powered Multimodal Construction Intelligence Platform

**Document Version:** 1.0.0  
**Status:** Approved for Baseline Design  
**Date:** 2026-10-25  
**Workspace:** `f:/BTech-CS-DS/vibe`  

---

## 1. Project Overview and Objectives

The **AI-Powered Multimodal Construction Intelligence Platform** is a centralized decision-support system designed for construction managers, civil engineers, site safety officers, quantity surveyors, and project stakeholders. 

The platform integrates multimodal Artificial Intelligence (computer vision and large language models) with domain-specific engineering heuristics to deliver automated site safety monitoring, structural crack diagnostics, real estate property valuation, quantity estimation and scheduling, context-aware chatbot assistance, daily log synthesis, and weather-driven operational advisories.

### Core Objectives
1. **Enhance Construction Safety:** Provide automated detection of PPE non-compliance and site hazard indicators from visual feeds.
2. **Accelerate Structural Assessment:** Standardize preliminary surface crack screening while distinguishing AI observations from formal structural engineering certification.
3. **Streamline Cost & Schedule Planning:** Deliver transparent, parametric quantity takeoff, cost estimation, and schedule synthesis.
4. **Context-Aware Field Assistance:** Synthesize field notes, daily logs, and dynamic meteorological hazards into operational recommendations.
5. **Architectural Separation & Strict Validation:** Enforce typed Pydantic contracts, explicit uncertainty signaling, and structured error handling across frontend and backend boundaries.

---

## 2. Intended Users and Persona Use Cases

| Persona | Role & Core Needs | Primary Platform Touchpoints |
|---|---|---|
| **Site Safety Officer** | Inspects daily visual footage; verifies PPE compliance (helmets, vests, boots) and spatial hazards (fall risks, excavations). | FR-01 (Safety Monitoring), FR-08 (Weather Advisory) |
| **Site / Civil Engineer** | Documents surface defects; checks cracking progression; tracks daily progress and material logistics. | FR-02 (Crack Analysis), FR-04 (Project Planning), FR-07 (Daily Site Assistant) |
| **Project Manager / Estimator** | Requires rapid estimates for material quantities, cost allocations, and milestone task scheduling. | FR-04 (Planning & Estimation), FR-03 (Valuation) |
| **Property Appraiser / Investor** | Evaluates real estate value based on location, area, construction age, and market variables. | FR-03 (Real Estate Valuation) |
| **Site Superintendent / Foreman** | Logs shift notes, reviews weather warnings, and queries safety/engineering guidelines. | FR-05 (Knowledge Assistant), FR-06 (Chatbot), FR-07 (Daily Assistant), FR-08 (Weather) |

---

## 3. High-Level Architecture & Interaction Flow

```
+------------------------------------------------------------------------------------+
|                                    REACT.JS FRONTEND                               |
|   +-------------------+  +--------------------+  +-------------------------------+ |
|   |   SafetyMonitor   |  |   CrackDetection   |  |           Valuation           | |
|   +-------------------+  +--------------------+  +-------------------------------+ |
|   |   ProjectPlanner  |  |   KnowledgeBase    |  |      ConstructionChatbot      | |
|   +-------------------+  +--------------------+  +-------------------------------+ |
|   | DailySiteAssistant|  |   WeatherAdvisor   |  | Multimodal Input / Nav (Vite) | |
|   +-------------------+  +--------------------+  +-------------------------------+ |
+------------------------------------------+-----------------------------------------+
                                           | HTTP / REST (JSON & Multipart)
                                           v
+------------------------------------------------------------------------------------+
|                                  FASTAPI BACKEND                                   |
|  +--------------------+  +--------------------+  +-------------------------------+ |
|  | Input Validation   |  |  Pydantic Schemas  |  |  Multipart & Vision Pipeline  | |
|  +--------------------+  +--------------------+  +-------------------------------+ |
|  | /api/safety/*      |  | /api/cracks/*      |  | /api/valuation/*              | |
|  | /api/planning/*    |  | /api/knowledge/*   |  | /api/chat/*                   | |
|  | /api/site/*        |  | /api/weather/*     |  | AI Provider Adapter Layer     | |
|  +--------------------+  +--------------------+  +-------------------------------+ |
+------------------------------------------+-----------------------------------------+
                                           | Secure SDK / REST (API Key Isolation)
                                           v
+------------------------------------------------------------------------------------+
|                           EXTERNAL SERVICES & AI PROVIDERS                         |
|  [ Multimodal Vision / LLM ]       [ Weather API ]       [ Image Gen / CAD / GIS ] |
+------------------------------------------------------------------------------------+
```

---

## 4. Detailed Functional Requirements

### FR-01: Construction Site Safety Monitoring
* **Description:** Ingest visual captures of construction areas to detect occupational health and safety hazards.
* **Functional Scope:**
  * Accept image formats (`JPEG`, `PNG`, `WEBP`) with optional textual annotations (e.g., location, zone, activity).
  * Identify visible PPE non-compliance (missing hard hats, high-visibility vests, protective eyewear/boots where discernable).
  * Identify environmental hazards: unprotected edges, scaffolding issues, trip hazards, proximity to heavy machinery.
  * Return structured findings with severity classifications (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), bounding observations, detailed explanations, and corrective action recommendations.
  * **Uncertainty & Ambiguity Handling:** Explicitly flag low-light, obscured, or low-resolution imagery with confidence scores; return an `uncertainty_note` whenever evidence is inconclusive.
  * **Compliance Disclaimer:** Every response MUST embed a non-negotiable disclaimer that the AI assessment does not constitute legal safety certification or replace certified OSHA/IS safety inspections.

### FR-02: Structural Crack Analysis
* **Description:** Perform surface-level visual inspection of cracks on concrete, masonry, plaster, and structural elements.
* **Functional Scope:**
  * Accept high-resolution imagery along with optional metadata (surface type: `concrete`, `brick_masonry`, `drywall`; orientation: `vertical`, `horizontal`, `diagonal`; location).
  * Detect and describe visible crack patterns (hairline, spider/crazing, longitudinal, shear, step cracks).
  * Provide preliminary severity rating (`COSMETIC`, `MONITOR`, `MODERATE_STRUCTURAL`, `SEVERE_STRUCTURAL`).
  * Hypothesize potential causes (thermal expansion, plastic shrinkage, settlement, structural overloading, corrosion).
  * Recommend follow-up procedures (e.g., crack width gauge monitoring, non-destructive ultrasonic testing, core sampling).
  * **Validation & Fallback:** Request sharper or closer images when optical resolution or lighting prevents reliable feature extraction.
  * **Professional Disclaimer:** Prominently declare that the AI diagnosis is preliminary screening and cannot substitute for an on-site licensed Structural Engineer's evaluation.

### FR-03: Real Estate Valuation
* **Description:** Calculate indicative market valuations for residential, commercial, and industrial properties based on location and physical attributes.
* **Functional Scope:**
  * Accept location parameters (city, locality, pincode), property type (`apartment`, `villa`, `commercial_office`, `plot`), built-up area (sq ft), carpet area, age of property (years), condition (`under_construction`, `new`, `good`, `renovation_needed`), and amenity parameters.
  * Estimate indicative property valuation expressed strictly in **Indian Rupees (₹)**.
  * Provide valuation metrics: estimated total value (₹), price per square foot (₹/sq.ft), low-to-high valuation band.
  * Itemize valuation factors and calculation weights (locality baseline, age depreciation rate, amenity markup, floor-rise premium).
  * Document all assumptions and analytical formulas used.
  * **Data Integrity Rule:** Prohibit generation of fictitious real estate comparables. Mark market trends as baseline estimates when live local registry records are unavailable.

### FR-04: Construction Project Planning
* **Description:** Automated parametric planning engine for material estimation, cost breakdown, and task schedule generation.
* **Functional Scope:**
  * Accept project dimensions (total built-up area, number of floors, footprint length × width, ceiling height), construction grade/type (`standard_residential`, `premium_residential`, `commercial_rcc`, `steel_structure`), and resource unit rates.
  * **Material Takeoff (MTO):** Compute required quantities of key materials:
    * Cement (bags / metric tons)
    * Structural Steel (metric tons)
    * Fine Aggregate / Sand (metric tons / cu ft)
    * Coarse Aggregate (metric tons / cu ft)
    * Bricks / AAC Blocks (units)
    * Paint & Finishes (liters)
  * **Cost Breakdown:** Calculate indicative expenditure in Indian Rupees (₹) across Materials, Labor, Equipment/Plant, Contingency (default 5-10%), and Taxes/Overheads.
  * **Task Schedule & Milestones:** Generate sequential work breakdown structure (WBS) with durations, precedence dependencies, and milestones (Foundation, Plinth, RCC Framing, Masonry, MEP, Finishing).
  * **Conceptual Architectural Visualization:** Interface with configured generative AI models to create conceptual exterior/interior render previews based on project specifications.
  * Explicitly output baseline coefficient assumptions and allow user overrides for unit rates.

### FR-05: Construction Knowledge Assistant
* **Description:** Searchable technical knowledge engine for civil engineering standards, building codes, and construction methodologies.
* **Functional Scope:**
  * Accept natural-language queries regarding IS codes (e.g., IS 456 for concrete, IS 800 for steel), ASTM/IBC equivalents, material specifications, and construction methodologies.
  * Provide structured, referenced answers with step-by-step methodologies and practical execution advice.
  * Distinguish general educational guidance from specific site-specific structural design calculations.
  * Support formatted export (Markdown/PDF report) when document generation services are configured.

### FR-06: Construction Chatbot
* **Description:** Interactive conversational assistant for ad-hoc civil engineering queries, site advice, and platform feature navigation.
* **Functional Scope:**
  * Maintain multi-turn conversational context using session identifiers (`session_id`).
  * Process natural-language site questions, material comparisons, and operational troubleshooting.
  * Detect ambiguous, vague, or underspecified queries and ask clarifying questions before answering.
  * Enforce safety guardrails: refuse unsafe demolition or structural shortcuts; provide standard warnings.
  * Gracefully handle context truncation and session timeouts.

### FR-07: Daily Site Assistant
* **Description:** Operational log aggregator that digests daily site reports, contractor updates, and delays into structured executive summaries.
* **Functional Scope:**
  * Ingest daily site notes: crew counts by trade, completed activities, material receipts, equipment downtime, and reported bottlenecks.
  * Parse and synthesize notes into structured progress summaries, identifying lagging tasks against the schedule.
  * Highlight operational risks (e.g., curing time conflicts, delivery delays, inspection blockers).
  * Provide actionable resource allocation and schedule recovery suggestions.
  * Maintain strict separation between user-reported site facts and AI-inferred recommendations.

### FR-08: Weather-Aware Advisory
* **Description:** Construction-specific meteorological advisor correlating weather forecasts with scheduled site activities.
* **Functional Scope:**
  * Fetch current conditions and short-term forecasts for the project location (temperature, humidity, precipitation probability, wind speed, UV index) via a configured weather service.
  * Correlate weather attributes with vulnerable construction activities:
    * Concrete pouring / curing (heat hydration risks, rain wash-out)
    * Cranes & high-altitude scaffolding (high wind gusts > 35 km/h)
    * Earthwork & excavation (heavy rain, soil collapse risk)
    * Painting & waterproofing (humidity > 85%, rain)
    * Welding & electrical works (lightning, rain)
  * Generate actionable precautions, shift rescheduling suggestions, and worker hydration/safety warnings.
  * Display forecast timestamps and data source attribution. Handle offline or failed API lookups gracefully without fabricating weather data.

### FR-09: Multimodal Input Handling
* **Description:** Universal input validation and ingestion pipeline across image, text, and structured tabular data.
* **Functional Scope:**
  * Validate uploaded files against allowed MIME types (`image/jpeg`, `image/png`, `image/webp`).
  * Enforce maximum upload size limit (default 10 MB per image, 25 MB per request batch).
  * Sanitize text inputs against script injection and buffer overruns.
  * Validate numerical ranges on project planning and valuation fields (e.g., built-up area > 0).
  * Route visual payloads exclusively to vision-capable multimodal models, falling back to text-only models when no imagery is attached.

### FR-10: Structured AI Responses
* **Description:** Contract-first API schema enforcement guaranteeing deterministic response structures.
* **Functional Scope:**
  * Every backend endpoint MUST validate incoming requests and outgoing responses using Pydantic models.
  * Enforce standard response wrapper containing `status` (`"success"` | `"partial"` | `"error"`), `data`, `meta` (model version, timestamp, latency), and `disclaimers`.
  * Validate and sanitize LLM raw completions with defensive parsing (strip Markdown fences, handle truncated JSON, enforce schema fallback).
  * Never assume an LLM output is valid JSON; provide robust validation error traps.
  * Include clear HTTP status codes (`200 OK`, `400 Bad Request`, `422 Unprocessable Entity`, `502 Bad Gateway`, `504 Gateway Timeout`).

---

## 5. User Interaction & Screen Workflows

1. **Dashboard / Navigation:** The user accesses a global responsive layout featuring sidebar/topbar navigation linking all eight primary modules.
2. **Analysis Workflows (Safety & Crack Detection):**
   * Drag-and-drop file upload zone with instant image preview.
   * Optional contextual inputs (location, notes, surface type).
   * Submit triggers an explicit loading indicator with status text.
   * Results panel displays severity badge, itemized findings with bounding references, actionable recommendations, and legal disclaimer.
3. **Planning & Valuation Workflows:**
   * Stepper or tabbed input forms with real-time numeric validation (built-up area, floors, unit rates).
   * Output renders interactive summary cards, cost itemization charts, and an editable task schedule table.
4. **Conversational Workflows (Chatbot & Knowledge Base):**
   * Persistent message thread with user/assistant avatars.
   * Suggested query chips for quick-start interactions.
   * Clarification prompts rendered as selectable option pills or direct text prompts.
5. **Site & Weather Log Workflows:**
   * Textarea/form for daily site notes paired with real-time weather summary cards.
   * Activity-impact matrix highlighting amber/red warnings for weather hazards.
