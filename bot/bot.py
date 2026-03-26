#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode for offline verification.

Usage:
    python bot.py --test "/command"           # Test mode with slash command
    python bot.py                             # Normal mode, connects to Telegram
"""

import argparse
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


def get_handler(command: str):
    """Map command to handler function."""
    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }
    base_command = command.split()[0].lower()
    if not base_command.startswith("/"):
        base_command = "/" + base_command
    return handlers.get(base_command)


def is_command(text: str) -> bool:
    """Check if text is a slash command."""
    return text.strip().startswith("/")


def run_test_mode(command: str) -> None:
    """Run handler in test mode and print response to stdout."""
    if is_command(command):
        handler = get_handler(command)
    else:
        print(f"Natural language queries coming in Task 3: '{command}'")
        sys.exit(0)

    if handler is None:
        print(f"Unknown command: {command}")
        print("Available commands: /start, /help, /health, /labs, /scores")
        sys.exit(0)

    parts = command.split()
    arg = parts[1] if len(parts) > 1 else None

    try:
        if arg:
            response = handler(arg)
        else:
            response = handler()
        print(response)
        sys.exit(0)
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)


def run_telegram_mode() -> None:
    """Run bot in normal Telegram mode."""
    print("Starting Telegram bot...")
    print("Telegram integration coming in Task 2.")
    print("For now, use test mode:")
    print("  python bot.py --test \"/start\"")
    sys.exit(0)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        epilog="Examples: python bot.py --test '/start'",
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run in test mode with specified command",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
