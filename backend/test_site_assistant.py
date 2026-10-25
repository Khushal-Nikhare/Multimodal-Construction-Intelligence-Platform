"""Offline contract tests for the Daily Site Assistant."""
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from routers.site_assistant import DailySiteAssistantRequest, _build_plan


class DailySiteAssistantTests(unittest.TestCase):
    @patch("routers.site_assistant.query_ai")
    def test_structured_site_plan_is_validated(self, mock_query_ai):
        mock_query_ai.return_value = """{
          "activity": "Concreting", "labour_count": 10, "site_condition": "Normal",
          "progress_summary": "Prepare the pour sequence.",
          "task_breakdown": [{"task": "Place concrete", "priority": "HIGH", "suggested_crew": 8, "execution_notes": "Use approved pour sequence."}],
          "required_materials_and_equipment": [{"item": "Concrete vibrator", "category": "EQUIPMENT", "purpose": "Consolidation."}],
          "safety_precautions": ["Use PPE."], "inspection_checklist": ["Check formwork."],
          "identified_delays": [], "operational_risks": [], "recommended_actions": ["Record slump test."],
          "disclaimer": "Indicative only."
        }"""
        data, used_fallback = _build_plan(DailySiteAssistantRequest(activity="Concreting", labour_count=10))
        self.assertFalse(used_fallback)
        self.assertEqual(data["task_breakdown"][0]["suggested_crew"], 8)

    @patch("routers.site_assistant.query_ai")
    def test_malformed_ai_output_uses_safe_partial_plan(self, mock_query_ai):
        mock_query_ai.return_value = "Start the work."
        data, used_fallback = _build_plan(DailySiteAssistantRequest(activity="Masonry", labour_count=6, site_condition="Rainy"))
        self.assertTrue(used_fallback)
        self.assertEqual(data["activity"], "Masonry")
        self.assertTrue(data["operational_risks"])

    def test_labour_count_is_bounded(self):
        with self.assertRaises(ValidationError):
            DailySiteAssistantRequest(activity="Concreting", labour_count=0)


if __name__ == "__main__":
    unittest.main()
