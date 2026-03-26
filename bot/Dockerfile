# Bot Dockerfile
# Uses uv and pyproject.toml exclusively (no requirements.txt)

FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy bot-specific files
COPY bot/pyproject.toml bot/uv.lock* ./

# Install dependencies
RUN uv sync --frozen 2>/dev/null || uv sync

# Copy bot source code
COPY bot/ ./bot/

# Set working directory to bot
WORKDIR /app/bot

# Run the bot
CMD ["uv", "run", "python", "bot.py"]