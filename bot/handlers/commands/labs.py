"""Handler for /labs command."""

from services.lms_client import LMSClient


def handle_labs() -> str:
    """Return list of available labs."""
    client = LMSClient()
    try:
        labs = client.get_labs()
        if not labs:
            return "No labs found."
        lab_list = "\n".join([f"• {lab.get('title', 'Unknown')}" for lab in labs])
        return f"Available labs:\n{lab_list}"
    except Exception as e:
        return f"❌ Backend error: {e}. Check that the services are running."
