"""Command handlers for the LMS Telegram bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram — same logic works from --test mode,
unit tests, or the Telegram bot.
"""

import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
