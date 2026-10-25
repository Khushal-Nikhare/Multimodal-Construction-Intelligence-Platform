# Requirements Traceability Matrix (RTM)
## AI-Powered Multimodal Construction Intelligence Platform

**Document Version:** 1.0.0  
**Status:** Baseline Inspection Complete  
**Date:** 2026-10-25  
**Workspace:** `f:/BTech-CS-DS/vibe`  

---

## 1. Traceability Matrix

The table below maps each documented requirement (functional and non-functional) to its associated frontend component, backend module/endpoint, planned verification method, and current codebase implementation status.

| Req ID | Requirement Name | Frontend Component | Backend Router / Service | Verification Method | Current Status | Notes & Gap Analysis |
|---|---|---|---|---|---|---|
| **FR-01** | Safety Monitoring | `frontend/src/components/SafetyMonitor.jsx` | `backend/routers/safety.py`<br>`backend/services/safety_service.py` | Vision model unit test + UI image upload test | **Planned** | Frontend component & backend router to be scaffolded. |
| **FR-02** | Structural Crack Analysis | `frontend/src/components/CrackDetection.jsx` | `backend/routers/cracks.py`<br>`backend/services/crack_service.py` | Crack image inference test + disclaimer check | **Planned** | To be implemented in subsequent milestones. |
| **FR-03** | Real Estate Valuation | `frontend/src/components/Valuation.jsx` | `backend/routers/valuation.py`<br>`backend/services/valuation_engine.py` | Unit test of valuation formulas (INR ₹ checks) | **Planned** | Form input validation & benchmark tables required. |
| **FR-04** | Project Planning & Estimation | `frontend/src/components/ProjectPlanner.jsx` | `backend/routers/planning.py`<br>`backend/services/planning_engine.py` | Quantity takeoff formula tests + schedule DAG tests | **Planned** | Parametric estimation engine with IS/CPWD coefficients. |
| **FR-05** | Construction Knowledge Base | `frontend/src/components/KnowledgeBase.jsx` | `backend/routers/knowledge.py`<br>`backend/services/knowledge_service.py` | Prompt test with civil engineering queries | **Planned** | Requires technical retrieval/prompting pipeline. |
| **FR-06** | Construction Chatbot | `frontend/src/components/ConstructionChatbot.jsx` | `backend/routers/chat.py`<br>`backend/services/chat_session.py` | Multi-turn session test + boundary clarification test | **Planned** | Chat UI and backend session store required. |
| **FR-07** | Daily Site Assistant | `frontend/src/components/DailySiteAssistant.jsx` | `backend/routers/site_assistant.py`<br>`backend/services/site_parser.py` | Log synthesis test (separating fact vs. inference) | **Planned** | Form interface for progress logs & delays. |
| **FR-08** | Weather-Aware Advisory | `frontend/src/components/WeatherAdvisor.jsx` | `backend/routers/weather.py`<br>`backend/services/weather_service.py` | Mock weather API test + activity risk matrix test | **Planned** | Open-Meteo or equivalent weather provider integration. |
| **FR-09** | Multimodal Input Handling | Reusable Upload Components (`frontend/src/components/common/`) | `backend/core/upload_handler.py`<br>`backend/core/middleware.py` | File size & MIME type validation tests | **Planned** | Enforce 10MB limit and JPEG/PNG/WEBP checks. |
| **FR-10** | Structured AI Responses | Global API client (`frontend/src/api/client.js`) | `backend/schemas/response_wrapper.py`<br>Pydantic schemas | JSON contract validation tests | **Planned** | Pydantic response models across all endpoints. |
| **NFR-01** | Reliability & Error Handling | React Error Boundary (`frontend/src/components/ErrorBoundary.jsx`) | `backend/core/exceptions.py`<br>FastAPI exception handlers | Simulated 5xx / timeout fault injection tests | **Planned** | Prevent uncaught exceptions in client & server. |
| **NFR-02** | Usability & Loading States | React Router Nav & Skeleton components | N/A | UX review & responsive mobile/desktop inspection | **Planned** | Clean navigation across 8 primary modules. |
| **NFR-03** | Maintainability & Clean Architecture | Modular directory structure (`frontend/src/`) | Clean 4-tier backend (`routers`, `schemas`, `services`, `core`) | Static linter / import structure verification | **Planned** | Separation of UI, business logic, and API calls. |
| **NFR-04** | Scalability & Provider Abstraction | Config-driven UI components | Provider Adapter Interface (`backend/services/ai_adapters/`) | Swappable provider test (mock vs. live LLM) | **Planned** | Abstract LLM/Vision interfaces to support multiple providers. |
| **NFR-05** | Security & Secret Isolation | Frontend `.env` check (no secrets) | `backend/core/config.py` (`pydantic-settings`) | Git leak detection + environment variable validation | **Planned** | Zero secret exposure in client-side bundles. |
| **NFR-06** | Performance & Response Targets | Client-side bundle size optimization | In-memory caching + asynchronous FastAPI handlers | Lighthouse audit + endpoint latency benchmarking | **Planned** | Sub-300ms parametric calculations; sub-5s vision calls. |
| **NFR-07** | Consistency & Contract Uniformity | Standardized response unwrapping | Global response wrapper middleware | Automated schema comparison tests | **Planned** | All responses use `status`, `data`, `error`, and `meta`. |
| **NFR-08** | Testability | Component test suite (Vitest) | Pytest test suite with mocked AI providers | CI pipeline execution | **Planned** | Schemas and calculation logic independently testable. |
| **NFR-09** | Transparency & Uncertainty Notes | Prominent badge/disclaimer UI components | Explicit `uncertainty_note` and `disclaimer` schema fields | Manual inspection of visual & calculation outputs | **Planned** | Ensure non-negotiable legal/engineering disclaimers. |

---

## 2. Codebase Baseline Inspection Findings

* **Workspace Path:** `f:/BTech-CS-DS/vibe`
* **Current Status:** Fresh workspace initialized for the platform implementation.
* **Inspected Assets:**
  * Verified that directory `docs/requirements/` has been established with complete functional specifications, non-functional quality standards, data contracts, acceptance criteria, and traceability mapping.
  * Verified that no orphan components or mock APIs are currently mislabeled as complete.
* **Readiness:** The requirements baseline is now established, paving the way for Activity 1.2 (`requirements.txt`, Python environment, and project directory structure).
