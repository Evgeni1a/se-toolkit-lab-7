"""Services for the LMS Telegram bot.

Provides clients for external APIs (LMS backend, LLM).
"""

from services.lms_client import LMSClient

__all__ = ["LMSClient"]
