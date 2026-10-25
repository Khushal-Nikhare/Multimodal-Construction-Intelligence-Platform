# Activity 6.1 — Integration Test Matrix

## Automated command

Run from `backend/` once a Python environment with `requirements.txt` installed is available:

```powershell
python -m unittest test_contracts test_chatbot test_site_assistant test_weather_service test_integration
```

The integration suite replaces external Groq and Open-Meteo calls with mocks. It verifies FastAPI routing, request parsing, response envelopes, and frontend-facing data shapes without API credentials.

## Recorded status — 2026-10-25

| Workflow | Test coverage | Latest result | Notes |
|---|---|---|---|
| Frontend production compilation | `npm run build` | Passed | Executed in this workspace. |
| Frontend static lint | `npm run lint` | Passed with 5 existing warnings | No lint errors. |
| Safety upload validation | `test_integration.test_safety_requires_an_image` | Not executed | Python interpreter unavailable in this workspace. |
| Crack upload validation | `test_integration.test_crack_rejects_non_image_upload` | Not executed | Python interpreter unavailable in this workspace. |
| Planning API contract | `test_integration.test_planning_plan_contract` | Not executed | Deterministic API path. |
| Valuation form contract | `test_integration.test_valuation_form_contract` | Not executed | INR response asserted. |
| Chatbot context/response contract | `test_integration.test_chatbot_preserves_conversation_contract` | Not executed | Groq mocked. |
| Daily site assistant contract | `test_integration.test_daily_site_assistant_contract` | Not executed | Groq mocked. |
| Weather advisory contract | `test_integration.test_weather_advisory_contract` | Not executed | Open-Meteo mocked. |
| Live Groq and Open-Meteo workflows | Manual smoke test | Not executed | Requires a Python runtime, backend server, network access, and valid provider configuration. |

## Manual browser smoke test

1. Start the FastAPI server from `backend/`: `uvicorn main:app --reload --port 8000`.
2. Start Vite from `frontend/`: `npm run dev`.
3. Confirm `/health` returns a success envelope, then test each visible module with valid and invalid input.
4. For Safety and Crack Analysis, use a JPEG/PNG/WebP under 10 MB, then retry with no file and a text file.
5. Submit a planner preset and valuation preset; verify values render without browser-console errors.
6. Send two chatbot turns; confirm the second answer receives prior context. Test a one-word query and a simulated provider failure.
7. Create a Daily Site plan with `Rainy` and verify either an AI plan or a labelled partial fallback.
8. Request a Weather Advisory for a known city; verify the source/timestamp display. Disconnect the provider or use an invalid city and verify no GO/NO-GO advice is rendered.
