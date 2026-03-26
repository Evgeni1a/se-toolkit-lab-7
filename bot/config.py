"""
Configuration loader for the bot.

Reads settings from environment variables (loaded from .env.bot.secret).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env.bot.secret from bot directory or parent directory
env_path = Path(__file__).parent / ".env.bot.secret"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env.bot.secret"
if env_path.exists():
    load_dotenv(env_path)


def get_lms_api_base_url() -> str:
    """Get LMS API base URL from environment."""
    # Default to Docker service name when running inside container
    return os.getenv("LMS_API_BASE_URL", "http://backend:8000")


def get_lms_api_key() -> str:
    """Get LMS API key from environment."""
    return os.getenv("LMS_API_KEY", "")


def get_bot_token() -> str:
    """Get Telegram bot token from environment."""
    return os.getenv("BOT_TOKEN", "")


def get_llm_api_key() -> str:
    """Get LLM API key from environment."""
    return os.getenv("LLM_API_KEY", "")


def get_llm_api_base_url() -> str:
    """Get LLM API base URL from environment."""
    return os.getenv("LLM_API_BASE_URL", "")


def get_llm_api_model() -> str:
    """Get LLM model name from environment."""
    return os.getenv("LLM_API_MODEL", "")