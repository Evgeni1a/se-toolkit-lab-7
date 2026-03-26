# Bot Dockerfile using uv for dependency management

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app/bot

# Copy bot project files
COPY bot/pyproject.toml /app/bot/pyproject.toml
COPY bot/uv.lock /app/bot/uv.lock
COPY bot/bot.py /app/bot/bot.py
COPY bot/config.py /app/bot/config.py
COPY bot/handlers/ /app/bot/handlers/
COPY bot/services/ /app/bot/services/

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Make sure environment is in PATH
ENV PATH="/app/bot/.venv/bin:$PATH"

# Switch to non-root user
USER nonroot

# Run the bot
CMD ["python", "bot.py"]
