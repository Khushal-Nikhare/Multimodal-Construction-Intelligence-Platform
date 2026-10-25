"""Offline weather-rule tests; external HTTP is mocked."""
import unittest
from unittest.mock import Mock, patch

from services.weather_service import build_advisory, fetch_weather


class WeatherServiceTests(unittest.TestCase):
    def test_rain_suspends_concreting(self):
        advisory = build_advisory("Concreting", {
            "city": "Bengaluru", "observed_at": "2026-10-25T09:00", "temperature_c": 27,
            "relative_humidity_percent": 82, "wind_speed_kmh": 12, "precipitation_mm": 1.2,
            "precipitation_probability_percent": 80, "weather_code": 61, "source": "Open-Meteo",
        })
        self.assertEqual(advisory["recommendation"], "SUSPEND_ACTIVITY")

    def test_strong_wind_suspends_lifting(self):
        advisory = build_advisory("Crane Lifting", {
            "city": "Mumbai", "observed_at": "2026-10-25T09:00", "temperature_c": 29,
            "relative_humidity_percent": 65, "wind_speed_kmh": 38, "precipitation_mm": 0,
            "precipitation_probability_percent": 0, "weather_code": 1, "source": "Open-Meteo",
        })
        self.assertEqual(advisory["recommendation"], "SUSPEND_ACTIVITY")

    @patch("services.weather_service.requests.get")
    def test_fetch_weather_maps_provider_response(self, mock_get):
        geocode = Mock(); geocode.json.return_value = {"results": [{"name": "Bengaluru", "latitude": 12.97, "longitude": 77.59}]}; geocode.raise_for_status.return_value = None
        forecast = Mock(); forecast.json.return_value = {"current": {"time": "2026-10-25T09:00", "temperature_2m": 27, "relative_humidity_2m": 70, "wind_speed_10m": 9, "precipitation": 0, "weather_code": 1}, "hourly": {"precipitation_probability": [10, 20]}}; forecast.raise_for_status.return_value = None
        mock_get.side_effect = [geocode, forecast]
        weather = fetch_weather("Bengaluru")
        self.assertEqual(weather["city"], "Bengaluru")
        self.assertEqual(weather["precipitation_probability_percent"], 20)


if __name__ == "__main__":
    unittest.main()
