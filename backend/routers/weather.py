"""FR-08 – Weather-aware construction advisory endpoints."""
import time
import uuid
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from schemas.contracts import WeatherAdvisoryData
from schemas.response import UniversalMeta, UniversalResponse
from services.weather_service import WeatherServiceError, build_advisory, fetch_weather

router = APIRouter(prefix="/api/weather", tags=["FR-08: Weather-Aware Advisory"])


async def _advisory(city: str, activity: str) -> UniversalResponse:
    started_at = time.time()
    try:
        weather = await run_in_threadpool(fetch_weather, city)
    except WeatherServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "error": {"code": "WEATHER_SERVICE_UNAVAILABLE", "message": str(exc)}},
        ) from exc

    data = WeatherAdvisoryData.model_validate(build_advisory(activity, weather)).model_dump()
    return UniversalResponse(
        status="success",
        data=data,
        meta=UniversalMeta(request_id=f"req-wth-{uuid.uuid4().hex[:8]}", latency_ms=round((time.time() - started_at) * 1000, 2), model_provider="open_meteo_rules"),
    )


@router.get("/advisory", response_model=UniversalResponse)
async def weather_advisory(
    city: str = Query(..., min_length=2, max_length=120),
    activity: str = Query(..., min_length=2, max_length=160),
):
    return await _advisory(city.strip(), activity.strip())


class LegacyWeatherAdvisorRequest(BaseModel):
    city: str = Field(..., min_length=2, max_length=120)
    activity: str = Field(..., min_length=2, max_length=160)


legacy_router = APIRouter(tags=["FR-08: Weather-Aware Advisory"])


@legacy_router.post("/api/weather-advisor", response_model=UniversalResponse, include_in_schema=False)
async def legacy_weather_advisor(payload: LegacyWeatherAdvisorRequest):
    """Compatibility endpoint; reported weather is intentionally not accepted as verified data."""
    return await _advisory(payload.city.strip(), payload.activity.strip())
