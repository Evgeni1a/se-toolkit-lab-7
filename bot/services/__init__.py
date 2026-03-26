"""Services for the LMS Telegram bot.

Provides clients for external APIs (LMS backend, LLM).
"""

from services.lms_client import LMSClient
from services.llm_client import LLMClient
from services.tools import ToolExecutor, TOOL_DEFINITIONS

__all__ = ["LMSClient", "LLMClient", "ToolExecutor", "TOOL_DEFINITIONS"]
