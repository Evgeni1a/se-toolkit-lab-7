# LMS Telegram Bot — Development Plan

## Overview

This document outlines the development plan for building a Telegram bot that lets users interact with the LMS backend through chat. The bot supports slash commands like `/health`, `/labs`, `/scores`, and understands plain language questions using an LLM for intent routing.

## Architecture

The bot follows a **separation of concerns** pattern:

```
┌─────────────────────────────────────────────────────────────┐
│  bot.py (Entry Point)                                       │
│  - Telegram client (aiogram)                                │
│  - CLI --test mode                                          │
├─────────────────────────────────────────────────────────────┤
│  handlers/ (Command Logic)                                  │
│  - Pure functions: input → text                             │
│  - No Telegram dependency                                   │
│  - Testable in isolation                                    │
├─────────────────────────────────────────────────────────────┤
│  services/ (External Integrations)                          │
│  - LMSClient: API calls to backend                          │
│  - LLMClient: Intent classification + tool use              │
├─────────────────────────────────────────────────────────────┤
│  config.py (Configuration)                                  │
│  - Environment variable loading                             │
│  - Secret management via .env.bot.secret                    │
└─────────────────────────────────────────────────────────────┘
```

## Task 1: Scaffold and Test Mode

**Goal:** Create project structure with testable handlers.

- `bot/` directory with entry point, handlers, services, config
- `--test` mode: `uv run bot.py --test "/command"` prints response to stdout
- Handlers are plain functions returning text — no Telegram dependency
- Same handler logic works from `--test`, unit tests, or Telegram

**Acceptance:** All placeholder commands work without crashes.

## Task 2: Backend Integration

**Goal:** Connect handlers to real LMS backend data.

- Implement `/health` — calls `GET /health` on backend
- Implement `/labs` — calls `GET /items/`, filters labs
- Implement `/scores <lab>` — calls analytics endpoint
- Error handling: backend down → friendly message, not crash
- API client uses Bearer auth with `LMS_API_KEY` from env vars

**Pattern:** Services layer abstracts HTTP calls. Handlers call services, not raw `httpx`.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Users can ask questions in plain language.

- LLM receives user message + tool descriptions
- LLM decides which tool to call (e.g., "get_labs", "get_scores")
- Tool results formatted and returned to user
- All 9 backend endpoints wrapped as LLM tools

**Key insight:** LLM routing depends on **tool description quality**, not prompt engineering. Descriptions must be clear about what each tool does and when to use it.

**Architecture:**
```
User: "what labs are available?"
    ↓
LLM (with tool descriptions)
    ↓
Tool call: get_labs()
    ↓
Format result → User
```

## Task 4: Containerize and Deploy

**Goal:** Bot runs in Docker alongside backend.

- Create `Dockerfile` for bot
- Add bot service to `docker-compose.yml`
- Bot uses service name `backend` for internal API calls (not `localhost`)
- Deploy to VM, verify with Telegram
- Document deployment in README

**Docker networking:** Containers communicate via service names. Bot connects to `http://backend:42002` not `localhost:42002`.

## Testing Strategy

1. **Unit tests:** Test handlers in isolation (pytest)
2. **Test mode:** Manual CLI testing with `--test` flag
3. **Integration tests:** Test full flow with mocked backend
4. **Manual testing:** Send commands in Telegram

## Security Considerations

- `.env.bot.secret` is gitignored — never commit secrets
- Bot token, API keys loaded from environment
- Bearer authentication for LMS API calls
- Error messages don't leak internal details

## Deployment Checklist

- [ ] `.env.bot.secret` exists on VM with all required values
- [ ] Bot service added to `docker-compose.yml`
- [ ] `docker compose up --build -d` starts all services
- [ ] Bot responds to `/start` in Telegram
- [ ] Backend health check passes
- [ ] Natural language queries work

## Future Improvements (Out of Scope)

- Response caching for expensive API calls
- Conversation context (multi-turn dialogues)
- Rich formatting (tables, charts as images)
- Inline keyboard buttons for common actions
