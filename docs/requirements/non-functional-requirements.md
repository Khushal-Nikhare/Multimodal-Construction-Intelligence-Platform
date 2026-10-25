# Non-Functional Requirements Specification (NFR)
## AI-Powered Multimodal Construction Intelligence Platform

**Document Version:** 1.0.0  
**Status:** Approved for Baseline Design  
**Date:** 2026-10-25  
**Workspace:** `f:/BTech-CS-DS/vibe`  

---

## 1. Overview and Quality Goals

Non-Functional Requirements (NFRs) define the operational quality, security, performance, maintainability, and resilience characteristics of the AI-Powered Multimodal Construction Intelligence Platform. These standards govern both frontend user experience and backend service engineering.

---

## 2. Detailed Non-Functional Requirements

### NFR-01: Reliability and Fault Tolerance
* **Error Containment:** All backend route handlers must be wrapped in error-handling middleware. Uncaught exceptions must return a standardized JSON error envelope rather than exposing stack traces.
* **Graceful Degradation:**
  * When an external AI provider fails or times out, the platform must return a partial response or a fallback advisory (e.g., standard heuristic estimates in planning; offline weather notices in weather advisor) with an explicit `partial` or `error` status.
  * In the frontend, component-level React Error Boundaries must prevent application-wide crashes if an individual module fails.
* **Network Resilience:** The frontend client must implement configurable retry policies (e.g., 2 retries with exponential backoff) for transient 5xx and network timeout errors.

### NFR-02: Usability and User Experience
* **Navigation Clarity:** Persistent navigation using React Router must allow seamless switching between modules without losing active form inputs where practical.
* **Loading and Progress States:** Every asynchronous operation (AI vision inference, weather fetch, planning calculation) must present immediate, visible feedback (skeleton loaders, animated progress bars, or disabled action buttons with spinner icons).
* **Responsive Layout:** The UI must be fully responsive across desktop (>= 1280px), tablet (768px - 1024px), and mobile viewports (>= 375px) using modern CSS flexbox and grid layouts.
* **Accessibility:** Form fields must have associated descriptive labels, accessible focus rings, and color contrast adhering to WCAG 2.1 Level AA (minimum 4.5:1 for normal text).

### NFR-03: Maintainability and Architecture
* **Modular Separation:**
  * **Frontend:** Maintain strict separation between UI view components, reusable layout elements, API service clients, and custom utility hooks.
  * **Backend:** Adhere to clean architecture:
    * `/routers` (FastAPI route controllers)
    * `/schemas` (Pydantic models for request/response validation)
    * `/services` (domain logic, AI provider wrappers, calculation engines)
    * `/core` (configuration, logging, security middleware)
* **Code Quality & Typing:**
  * Frontend: Standardized ECMAScript modules with clear prop validation.
  * Backend: Strict Python type hinting (`typing`, `pydantic`) checked via static linters (`ruff` / `mypy`).
* **Configuration Management:** All environment-specific variables (ports, hostnames, API endpoints) must be externalized in `.env` files and validated via `pydantic-settings`.

### NFR-04: Scalability and Extensibility
* **Stateless Backend Design:** FastAPI application instances must remain stateless, allowing horizontal scaling behind standard load balancers.
* **Provider Abstraction:** AI service integrations (OpenAI, Google Gemini, Anthropic, local Ollama) must sit behind unified adapter interfaces (e.g., `BaseVisionModel`, `BaseLLMModel`) so that model providers can be swapped or cascaded without altering domain controllers.
* **Modular Feature Registration:** New feature modules can be attached simply by mounting a new FastAPI router and adding a corresponding React route.

### NFR-05: Security and Privacy
* **Secret Isolation:** API keys, database credentials, and service tokens must NEVER be exposed in frontend bundles or committed to source control. All external AI calls must originate from the FastAPI backend.
* **Input Sanitization & File Upload Security:**
  * File uploads must be checked by inspecting both Content-Type headers and binary magic numbers to prevent malicious script uploads.
  * Uploaded images must be processed in-memory or stored in isolated temporary directories with strict access permissions.
  * Text inputs must be sanitized to mitigate Cross-Site Scripting (XSS) and prompt injection vulnerabilities.
* **CORS Policy:** Strict Cross-Origin Resource Sharing (CORS) configuration in FastAPI limiting allowed origins to the frontend development server (`http://localhost:5173` or production domain).

### NFR-06: Performance and Latency Targets
* **Frontend Render Time:** Initial page load and first contentful paint (FCP) must complete within **1.5 seconds** over standard broadband.
* **Deterministic API Endpoints:** Algorithmic calculation endpoints (e.g., property valuation formulas, material takeoff heuristics) must respond in under **300 ms** (p95).
* **Multimodal AI Vision Latency:** Image-based analysis endpoints (Safety monitoring, Crack detection) must return structured outputs within **5.0 seconds** (p90), subject to external model provider round-trip limits.
* **Weather & Real-Time Lookups:** Cached weather advisories must respond in under **200 ms** (cache hit) or **1.5 seconds** (external API fetch).

### NFR-07: Consistency and Contract Uniformity
* **Unified API Response Schema:** Every API response must conform to a standardized wrapper:
  ```json
  {
    "status": "success",
    "data": {},
    "error": null,
    "meta": {
      "timestamp": "2026-10-25T12:00:00Z",
      "model": "gemini-1.5-pro",
      "execution_time_ms": 320
    }
  }
  ```
* **Consistent Status Codes:** Strict semantic use of HTTP status codes (`200 OK`, `400 Bad Request`, `422 Validation Error`, `500 Internal Error`, `503 Service Unavailable`).

### NFR-08: Testability
* **Independent Testability:**
  * Pydantic schemas must be unit-testable against valid and malformed payloads without invoking network calls.
  * AI service wrappers must implement mockable test doubles to allow deterministic offline testing of routers and business logic.
  * React components must be testable using standard tools (Vitest / React Testing Library) with mocked API responses.

### NFR-09: Transparency and Explainability
* **Model Uncertainty:** Any probabilistic inference from vision or LLM models must clearly communicate uncertainty bands or confidence ratings.
* **Auditability:** Material planning calculations and property valuation formulas must expose their arithmetic steps and baseline assumptions (e.g., cement consumption coefficient: 0.4 bags/sq.ft).
* **Mandatory Legal Disclaimers:** AI outputs must render clear disclaimers that predictions do not supersede certified human architectural, engineering, or legal audits.

---

## 3. Measurable Acceptance Criteria Summary

| Metric | Target | Measurement Method |
|---|---|---|
| Frontend First Contentful Paint | < 1.5 seconds | Lighthouse audit / Chrome DevTools |
| Parametric Endpoint Latency | < 300 ms (p95) | FastAPI middleware timer |
| Multimodal AI Response Latency | < 5.0 seconds (p90) | External API instrumentation |
| Backend Schema Test Coverage | 100% on request/response models | Pytest test suite |
| Error Envelope Uniformity | 100% compliance across all endpoints | Contract verification tests |
| WCAG Accessibility Rating | Level AA compliant | Axe DevTools / Lighthouse |
