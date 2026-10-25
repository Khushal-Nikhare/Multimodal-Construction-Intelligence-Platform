from typing import Any, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class UniversalMeta(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    request_id: Optional[str] = None
    latency_ms: Optional[float] = None
    model_provider: Optional[str] = "groq"

class UniversalError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class UniversalResponse(BaseModel):
    status: str = "success"  # "success" | "partial" | "error"
    data: Optional[Any] = None
    error: Optional[UniversalError] = None
    meta: UniversalMeta = Field(default_factory=UniversalMeta)
