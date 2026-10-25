"""Application-level API contract tests with AI and weather providers mocked.

Run from the backend directory:
    python -m unittest test_integration
"""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


WEATHER_FIXTURE = {
    "city": "Bengaluru",
    "observed_at": "2026-10-25T09:00",
    "temperature_c": 27.0,
    "relative_humidity_percent": 70.0,
    "wind_speed_kmh": 8.0,
    "precipitation_mm": 0.0,
    "precipitation_probability_percent": 10,
    "weather_code": 1,
    "source": "Open-Meteo",
}


class PlatformIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_envelope(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertIn("groq_configured", response.json()["data"])

    def test_planning_plan_contract(self):
        response = self.client.post("/api/planning/plan", json={
            "built_up_area_sqft": 2400,
            "floors": 2,
            "construction_grade": "standard_residential",
            "city": "Bengaluru",
        })
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertIn("materials", body["data"])
        self.assertIn("cost", body["data"])
        self.assertIn("schedule", body["data"])

    def test_valuation_form_contract(self):
        response = self.client.post("/api/real-estate-valuation", data={
            "city": "Bengaluru", "locality": "Whitefield", "built_up_area_sqft": "1450",
            "property_type": "residential_apartment", "age_years": "4",
        })
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["data"]["currency"], "INR")
        self.assertGreater(body["data"]["estimated_total_value"], 0)

    def test_safety_requires_an_image(self):
        response = self.client.post("/api/safety/analyze")
        self.assertEqual(response.status_code, 422)

    def test_crack_rejects_non_image_upload(self):
        response = self.client.post("/api/cracks/analyze", files={"image": ("notes.txt", b"not an image", "text/plain")})
        self.assertEqual(response.status_code, 415)

    @patch("routers.chatbot.query_ai")
    def test_chatbot_preserves_conversation_contract(self, mock_query_ai):
        mock_query_ai.return_value = """{
          "session_id": "sess-integration", "reply": "Use the approved stripping schedule.",
          "requires_clarification": false, "action_suggestions": ["Check slab span"],
          "suggested_followups": ["What is the concrete grade?"]
        }"""
        response = self.client.post("/api/chatbot", json={
            "message": "Can I remove props?", "session_id": "sess-integration",
            "history": [{"role": "user", "content": "We poured a slab yesterday."}],
        })
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["session_id"], "sess-integration")
        self.assertTrue(body["action_suggestions"])

    @patch("routers.site_assistant.query_ai")
    def test_daily_site_assistant_contract(self, mock_query_ai):
        mock_query_ai.return_value = """{
          "activity": "Concreting", "labour_count": 10, "site_condition": "Normal",
          "progress_summary": "Prepare the pour sequence.",
          "task_breakdown": [{"task": "Place concrete", "priority": "HIGH", "suggested_crew": 8, "execution_notes": "Use approved sequence."}],
          "required_materials_and_equipment": [], "safety_precautions": ["Use PPE."],
          "inspection_checklist": ["Check formwork."], "identified_delays": [], "operational_risks": [],
          "recommended_actions": ["Record slump test."], "disclaimer": "Indicative only."
        }"""
        response = self.client.post("/api/site-assistant", json={"activity": "Concreting", "labour_count": 10, "site_condition": "Normal"})
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["data"]["task_breakdown"][0]["suggested_crew"], 8)

    @patch("routers.weather.fetch_weather", return_value=WEATHER_FIXTURE)
    def test_weather_advisory_contract(self, mock_fetch_weather):
        response = self.client.get("/api/weather/advisory", params={"city": "Bengaluru", "activity": "Slab Concreting"})
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["data"]["weather"]["source"], "Open-Meteo")
        self.assertIn(body["data"]["recommendation"], {"SAFE_TO_PROCEED", "PROCEED_WITH_PRECAUTIONS", "SUSPEND_ACTIVITY"})


if __name__ == "__main__":
    unittest.main()
