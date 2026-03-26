"""Handler for /scores command."""

from services.lms_client import LMSClient


def handle_scores(lab_name: str = None) -> str:
    """Return pass rates for a specific lab.
    
    Args:
        lab_name: The lab name to get scores for.
        
    Returns:
        Pass rates information or error message.
    """
    if not lab_name:
        return "Please specify a lab name. Example: /scores Lab 1"
    
    # Placeholder - will be implemented in Task 2
    return f"Pass rates for '{lab_name}': Coming soon in Task 2!"
