# Acceptance Criteria Specification
## AI-Powered Multimodal Construction Intelligence Platform

**Document Version:** 1.0.0  
**Status:** Approved for Baseline Design  
**Date:** 2026-10-25  
**Workspace:** `f:/BTech-CS-DS/vibe`  

---

## 1. Overview

This document specifies testable acceptance criteria for each functional requirement (FR-01 through FR-10) using Given-When-Then (Gherkin style) scenarios. It covers positive paths, negative/invalid input flows, and edge cases.

---

## 2. Detailed Functional Acceptance Criteria

### FR-01: Construction Site Safety Monitoring

* **Scenario 1.1 (Positive - Clear PPE & Hazard Detection):**
  * **Given** an image depicting workers without hard hats near an unprotected slab edge,
  * **When** submitted to `POST /api/safety/analyze`,
  * **Then** the response status is `200 OK` with `status: "success"`,
  * **And** the `hazards_identified` array lists missing hard hats (`PPE_NON_COMPLIANCE`) and unprotected edge (`FALL_HAZARD`),
  * **And** each item includes a severity rating (`HIGH` or `CRITICAL`) and recommended corrective action,
  * **And** a mandatory non-certification safety disclaimer is attached.

* **Scenario 1.2 (Negative - Unsupported File Format / Oversized File):**
  * **Given** a user uploads a `.pdf` file or a 15 MB image,
  * **When** submitted to `POST /api/safety/analyze`,
  * **Then** the server responds with HTTP `400 Bad Request` or `422 Unprocessable Entity`,
  * **And** the standardized error envelope states `"INVALID_IMAGE_PAYLOAD"` with clear file constraints.

* **Scenario 1.3 (Edge Case - Blurry / Obscured / Dark Imagery):**
  * **Given** an underexposed or severely blurred site image,
  * **When** submitted to `POST /api/safety/analyze`,
  * **Then** the platform returns `status: "success"` or `"partial"`,
  * **And** includes an explicit `uncertainty_note` advising the user that image quality is insufficient for conclusive PPE verification.

---

### FR-02: Structural Crack Analysis

* **Scenario 2.1 (Positive - Crack Diagnostic):**
  * **Given** a high-resolution image of a 45-degree diagonal crack on an RCC beam,
  * **When** submitted to `POST /api/cracks/analyze` with `surface_type: "concrete"`,
  * **Then** the response identifies the crack pattern as shear/diagonal,
  * **And** returns a preliminary severity (`MODERATE_STRUCTURAL`), plausible engineering causes, and recommended follow-up actions (e.g., crack width gauge, structural engineer inspection),
  * **And** includes a disclaimer distinguishing AI screening from professional engineering certification.

* **Scenario 2.2 (Negative - Non-Structural / Blank Image):**
  * **Given** an image of an untextured blank surface or completely unrelated object (e.g., a car),
  * **When** submitted to `POST /api/cracks/analyze`,
  * **Then** the response indicates `crack_detected: false` with an advisory note explaining that no structural crack features were identified.

* **Scenario 2.3 (Edge Case - Distant / Indistinct Pattern):**
  * **Given** an image taken from too great a distance to measure crack width,
  * **When** submitted to the endpoint,
  * **Then** the `image_quality_assessment` advises the user to capture close-up images with a reference scale.

---

### FR-03: Real Estate Valuation

* **Scenario 3.1 (Positive - Standard Valuation):**
  * **Given** valid property inputs (`city: "Bengaluru"`, `locality: "Whitefield"`, `built_up_area_sqft: 1450`, `property_type: "residential_apartment"`, `age_years: 4`),
  * **When** submitted to `POST /api/valuation/estimate`,
  * **Then** the response returns total value in Indian Rupees (₹),
  * **And** includes rate per sq.ft in ₹ and a low-to-high valuation band,
  * **And** itemizes adjustment factors (locality baseline, age depreciation, floor premium).

* **Scenario 3.2 (Negative - Negative or Zero Area):**
  * **Given** an input payload with `built_up_area_sqft: -100` or `0`,
  * **When** submitted to `POST /api/valuation/estimate`,
  * **Then** the server responds with HTTP `422 Unprocessable Entity` citing that area must be greater than zero.

* **Scenario 3.3 (Edge Case - Unrecognized Locality):**
  * **Given** a rural or unindexed locality name,
  * **When** submitted to the endpoint,
  * **Then** the platform applies district/tier-level benchmark defaults,
  * **And** appends an explanatory note highlighting the wider valuation variance.

---

### FR-04: Construction Project Planning

* **Scenario 4.1 (Positive - Material Takeoff & Cost Breakdown):**
  * **Given** valid inputs (`built_up_area_sqft: 3000`, `floors: 2`),
  * **When** submitted to `/api/planning/materials`,
  * **Then** the response details quantities for Cement (bags), Steel (tons), Sand, Aggregate, and Bricks,
  * **And** the corresponding `/api/planning/cost` call computes material, labor, and contingency costs in ₹.

* **Scenario 4.2 (Positive - Schedule Generation):**
  * **Given** the same project parameters,
  * **When** submitted to `/api/planning/schedule`,
  * **Then** the response outputs a sequenced list of project phases with durations and dependencies.

* **Scenario 4.3 (Negative - Unrealistic Floor / Area Combination):**
  * **Given** an input with `built_up_area_sqft: 500` and `floors: 50` (unfeasible structural density without special configuration),
  * **When** submitted to the planning endpoint,
  * **Then** the system validates parameters or returns an advisory warning concerning high-rise structural feasibility.

---

### FR-05: Construction Knowledge Assistant

* **Scenario 5.1 (Positive - Technical Standard Query):**
  * **Given** a user asks `"What is the minimum curing period under IS 456?"`,
  * **When** sent to `POST /api/knowledge/ask`,
  * **Then** the system returns the correct technical duration (7 days for OPC; 10-14 days for blended/hot weather),
  * **And** cites the relevant standard (IS 456:2000 Clause 13.5).

* **Scenario 5.2 (Negative - Empty Query):**
  * **Given** an empty string query payload,
  * **When** sent to the endpoint,
  * **Then** the server returns HTTP `422 Unprocessable Entity`.

---

### FR-06: Construction Chatbot

* **Scenario 6.1 (Positive - Multi-turn Conversation):**
  * **Given** an active `session_id` and previous context discussing foundation excavation,
  * **When** the user asks `"What if we hit groundwater at 2 meters?"`,
  * **Then** the chatbot generates context-aware advice on dewatering pumps, sump pits, and soil stability.

* **Scenario 6.2 (Edge Case - Ambiguous Query):**
  * **Given** a user inputs a single word `"Concrete"`,
  * **When** sent to `POST /api/chat`,
  * **Then** the chatbot detects ambiguity and returns a helpful clarifying prompt with suggested sub-topics (mix design, curing, testing).

---

### FR-07: Daily Site Assistant

* **Scenario 7.1 (Positive - Progress & Delay Synthesis):**
  * **Given** raw site notes indicating delayed steel delivery and 8 workers present,
  * **When** submitted to `POST /api/site-assistant/analyze`,
  * **Then** the system outputs a concise progress summary, isolates the delivery delay risk, and suggests work resequencing.

* **Scenario 7.2 (Integrity Check - Fact Separation):**
  * **Given** user-submitted site notes,
  * **When** analyzed,
  * **Then** the response clearly separates user-provided facts from AI-generated recommendations.

---

### FR-08: Weather-Aware Advisory

* **Scenario 8.1 (Positive - Weather Advisory with Activity Correlation):**
  * **Given** `city: "Bengaluru"` and `activity: "concreting"` during forecast rain,
  * **When** requested via `GET /api/weather/advisory`,
  * **Then** the advisory returns current temperature/humidity/precipitation and provides tailored warnings (washout risk, tarpaulin protection).

* **Scenario 8.2 (Negative / Fallback - Weather Service Offline):**
  * **Given** external weather provider downtime,
  * **When** requested,
  * **Then** the API returns a graceful fallback with `status: "partial"` or cached data without crashing or inventing synthetic meteorological figures.

---

### FR-09: Multimodal Input Handling

* **Scenario 9.1 (File Type Validation):**
  * **Given** an upload with mime-type `application/x-executable` or disguised `.exe`,
  * **When** processed by the backend middleware,
  * **Then** it is rejected immediately with HTTP `415 Unsupported Media Type` or `400 Bad Request`.

---

### FR-10: Structured AI Responses

* **Scenario 10.1 (Schema Conformance):**
  * **Given** any backend API endpoint,
  * **When** called under both success and failure conditions,
  * **Then** the response payload matches the universal schema (`status`, `data`, `error`, `meta`) with valid HTTP status codes.
