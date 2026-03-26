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
        return "Please specify a lab name. Example: /scores lab-04"

    client = LMSClient()
    try:
        pass_rates = client.get_pass_rates(lab_name)
        
        if pass_rates is None:
            return f"Lab '{lab_name}' not found. Use /labs to see available labs."
        
        if not pass_rates:
            return f"No pass rate data available for '{lab_name}'."
        
        lines = [f"Pass rates for {lab_name}:"]
        for task in pass_rates:
            task_name = task.get("task_name", task.get("task", "Unknown"))
            pass_rate = task.get("pass_rate", task.get("passRate", 0))
            attempts = task.get("attempts", 0)
            lines.append(f"• {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Backend error: {e}. Check that the services are running."
