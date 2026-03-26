"""Command handlers for the LMS Telegram bot."""

from handlers.commands.start import handle_start
from handlers.commands.help import handle_help
from handlers.commands.health import handle_health
from handlers.commands.labs import handle_labs
from handlers.commands.scores import handle_scores

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
