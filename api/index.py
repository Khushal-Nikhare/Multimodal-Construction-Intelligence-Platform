"""Vercel entrypoint for the FastAPI application."""

import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_path))

from main import app

__all__ = ["app"]
