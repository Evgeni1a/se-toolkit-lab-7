"""Tool definitions and executor for LLM-based intent routing."""

import sys
from typing import List, Dict, Any, Optional

from services.lms_client import LMSClient


# Tool schemas for LLM
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks in the LMS",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average pass rates and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day timeline for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, e.g. 5"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker API",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You can fetch data about labs, students, scores, and analytics using the provided tools.

When the user asks a question:
1. First understand what information they need
2. Call the appropriate tool(s) to fetch the data
3. Analyze the results and provide a clear, helpful answer

If the user asks about:
- Available labs → use get_items
- Scores or pass rates for a specific lab → use get_pass_rates with the lab name
- Top students → use get_top_learners
- Group performance → use get_groups
- Completion rates → use get_completion_rate
- Timeline of submissions → use get_timeline
- All students → use get_learners
- Refreshing data → use trigger_sync

For comparison questions (e.g., "which lab has the lowest pass rate"):
1. First get all labs with get_items
2. Then get pass rates for each lab
3. Compare and provide the answer with specific numbers

Be concise but informative. Always include specific numbers from the data when available.
If you don't understand the question, ask for clarification or suggest what you can help with.
"""


class ToolExecutor:
    """Executes tool calls by invoking the appropriate LMS API methods."""

    def __init__(self, lms_client: LMSClient = None):
        """Initialize the tool executor.

        Args:
            lms_client: LMS client for API calls.
        """
        self.lms_client = lms_client or LMSClient()

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool call.

        Args:
            name: Tool name (e.g., 'get_items', 'get_pass_rates').
            arguments: Tool arguments dict.

        Returns:
            Tool execution result.
        """
        method_name = f"_tool_{name}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(**arguments)
        else:
            return {"error": f"Unknown tool: {name}"}

    def _tool_get_items(self) -> List[Dict[str, Any]]:
        """Get all items (labs and tasks)."""
        return self.lms_client.get_items()

    def _tool_get_learners(self) -> List[Dict[str, Any]]:
        """Get all learners."""
        try:
            return self.lms_client.get_learners()
        except Exception as e:
            return {"error": str(e)}

    def _tool_get_scores(self, lab: str) -> Any:
        """Get score distribution for a lab."""
        try:
            return self.lms_client.get_scores(lab)
        except Exception as e:
            return {"error": str(e)}

    def _tool_get_pass_rates(self, lab: str) -> Any:
        """Get pass rates for a lab."""
        return self.lms_client.get_pass_rates(lab)

    def _tool_get_timeline(self, lab: str) -> Any:
        """Get timeline for a lab."""
        try:
            return self.lms_client.get_timeline(lab)
        except Exception as e:
            return {"error": str(e)}

    def _tool_get_groups(self, lab: str) -> Any:
        """Get group performance for a lab."""
        try:
            return self.lms_client.get_groups(lab)
        except Exception as e:
            return {"error": str(e)}

    def _tool_get_top_learners(self, lab: str, limit: int = 5) -> Any:
        """Get top learners for a lab."""
        try:
            return self.lms_client.get_top_learners(lab, limit=limit)
        except Exception as e:
            return {"error": str(e)}

    def _tool_get_completion_rate(self, lab: str) -> Any:
        """Get completion rate for a lab."""
        try:
            return self.lms_client.get_completion_rate(lab)
        except Exception as e:
            return {"error": str(e)}

    def _tool_trigger_sync(self) -> Any:
        """Trigger ETL sync."""
        try:
            return self.lms_client.trigger_sync()
        except Exception as e:
            return {"error": str(e)}
