"""Handler for /health command."""

from services.lms_client import LMSClient


def handle_health() -> str:
    """Check backend health status."""
    client = LMSClient()
    result = client.health_check()
    
    if result.get("healthy"):
        item_count = result.get("item_count", 0)
        return f"✅ Backend is healthy. {item_count} items available."
    else:
        error = result.get("error", "unknown error")
        return f"❌ Backend error: {error}. Check that the services are running."
