"""Handler for /health command."""

import os
from services.lms_client import LMSClient


def handle_health() -> str:
    """Check backend health status."""
    client = LMSClient()
    try:
        is_healthy = client.health_check()
        if is_healthy:
            return "✅ Backend is healthy"
        else:
            return "❌ Backend returned unhealthy status"
    except Exception as e:
        return f"❌ Backend is unavailable: {e}"
