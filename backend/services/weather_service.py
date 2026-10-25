"""Open-Meteo client and deterministic construction-weather risk rules."""
from typing import Any, Dict, List

import requests

from core.config import settings

REQUEST_TIMEOUT_SECONDS = 10
RAIN_SENSITIVE_ACTIVITIES = {"concreting", "excavation", "roofing", "waterproofing", "painting", "plastering"}
WIND_SENSITIVE_ACTIVITIES = {"crane lifting", "lifting", "scaffolding", "work at height", "roofing"}


class WeatherServiceError(RuntimeError):
    """Raised when current provider data cannot be fetched or understood."""


def _get_city_coordinates(city: str) -> Dict[str, Any]:
    response = requests.get(
        settings.WEATHER_GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        raise WeatherServiceError(f"No weather location was found for '{city}'.")
    return results[0]


def fetch_weather(city: str) -> Dict[str, Any]:
    try:
        place = _get_city_coordinates(city)
        response = requests.get(
            settings.WEATHER_API_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
                "hourly": "precipitation_probability",
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        current = payload.get("current")
        probabilities = (payload.get("hourly") or {}).get("precipitation_probability") or []
        if not current or not all(key in current for key in ("temperature_2m", "wind_speed_10m", "precipitation", "weather_code", "time")):
            raise WeatherServiceError("Weather provider returned incomplete current-condition data.")
        return {
            "city": place.get("name", city),
            "observed_at": current["time"],
            "temperature_c": float(current["temperature_2m"]),
            "relative_humidity_percent": float(current.get("relative_humidity_2m", 0)),
            "wind_speed_kmh": float(current["wind_speed_10m"]),
            "precipitation_mm": float(current["precipitation"]),
            "precipitation_probability_percent": int(max(probabilities[:6], default=0)),
            "weather_code": int(current["weather_code"]),
            "source": "Open-Meteo",
        }
    except WeatherServiceError:
        raise
    except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
        raise WeatherServiceError("Current weather data could not be retrieved from the configured provider.") from exc


def build_advisory(activity: str, weather: Dict[str, Any]) -> Dict[str, Any]:
    normalized_activity = activity.strip().lower()
    risks: List[str] = []
    precautions: List[str] = []
    mitigation: List[str] = []
    recommendation = "SAFE_TO_PROCEED"
    reason = "No configured stop threshold is exceeded in the current observation and near-term precipitation forecast."

    rain_risk = weather["precipitation_mm"] > 0 or weather["precipitation_probability_percent"] >= 60
    if normalized_activity in RAIN_SENSITIVE_ACTIVITIES and rain_risk:
        recommendation = "SUSPEND_ACTIVITY"
        reason = "Rainfall is observed or likely in the next six hours for a rain-sensitive activity."
        risks.append("Rain can compromise work quality, access, electrical safety, or excavation stability.")
        precautions.append("Do not begin the exposed activity until the work area is dry and protected.")
        mitigation.append("Resequence indoor/protected work and protect exposed materials and fresh work with approved covers.")
    elif weather["precipitation_probability_percent"] >= 30:
        recommendation = "PROCEED_WITH_PRECAUTIONS"
        reason = "Near-term precipitation probability warrants weather protection and monitoring."
        risks.append("Changing weather may interrupt exposed work and make access surfaces slippery.")
        precautions.append("Confirm drainage, electrical protection, and rain covers before mobilising the crew.")
        mitigation.append("Monitor the forecast at shift start and before each exposed work phase.")

    if normalized_activity in WIND_SENSITIVE_ACTIVITIES and weather["wind_speed_kmh"] >= 35:
        recommendation = "SUSPEND_ACTIVITY"
        reason = "Observed wind is at or above the configured 35 km/h stop threshold for wind-sensitive work."
        risks.append("Strong wind can destabilise suspended loads, scaffolding, and workers at height.")
        precautions.append("Stop lifting and exposed height work; secure loose materials and exclusion zones.")
        mitigation.append("Resume only after wind readings are within equipment and approved method-statement limits.")
    elif normalized_activity in WIND_SENSITIVE_ACTIVITIES and weather["wind_speed_kmh"] >= 25 and recommendation != "SUSPEND_ACTIVITY":
        recommendation = "PROCEED_WITH_PRECAUTIONS"
        reason = "Elevated wind requires equipment-limit checks and close site supervision."
        risks.append("Wind gusts can affect load control and worker stability.")
        precautions.append("Check the crane/equipment manufacturer limits and use a competent banksman.")

    if weather["temperature_c"] >= 38:
        risks.append("High temperature increases heat-stress risk and can affect fresh concrete handling.")
        precautions.append("Schedule hydration, shaded rest breaks, and increased supervision for heat-stress symptoms.")
        mitigation.append("Move strenuous tasks to cooler periods where approved and protect temperature-sensitive materials.")
        if recommendation == "SAFE_TO_PROCEED":
            recommendation = "PROCEED_WITH_PRECAUTIONS"
            reason = "High temperature requires heat-stress and quality-control measures."

    return {
        "activity": activity,
        "recommendation": recommendation,
        "recommendation_reason": reason,
        "weather": weather,
        "weather_related_risks": risks,
        "safety_precautions": precautions or ["Complete the normal pre-start safety inspection and monitor changing conditions."],
        "mitigation_steps": mitigation or ["Record the weather check in the daily site log and reassess if conditions change."],
        "data_freshness_note": "Uses the provider's current observation and the highest precipitation probability in the next six forecast hours.",
    }
