# Fix: backend/Dockerfile uv workspace mount issue

## Problem

When building the backend Docker image, the `uv sync --locked --no-install-project` command failed because `bot/pyproject.toml` was not mounted during the initial dependency sync.

## Root Cause

The Dockerfile uses a multi-stage build with `uv` for dependency management. The first stage runs:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/pyproject.toml,target=backend/pyproject.toml \
    --mount=type=bind,source=bot/pyproject.toml,target=bot/pyproject.toml \
    uv sync --locked --no-install-project
```

The `--no-install-project` flag tells uv to sync dependencies without installing the project itself. However, uv needs **all** `pyproject.toml` files from the workspace to resolve dependencies correctly.

Without the `bot/pyproject.toml` mount, uv couldn't resolve the workspace dependencies, causing the build to fail.

## Solution

Two changes were required in `backend/Dockerfile`:

### 1. Add mount for bot/pyproject.toml in first uv sync

```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/pyproject.toml,target=backend/pyproject.toml \
    --mount=type=bind,source=bot/pyproject.toml,target=bot/pyproject.toml \
    uv sync --locked --no-install-project
```

### 2. Add COPY for bot/pyproject.toml before second uv sync

```dockerfile
# Copy the entire project
COPY . /app

# Install the project (without --reinstall, use --locked)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
```

The `COPY . /app` copies all files including `bot/pyproject.toml`, so the second `uv sync --locked` can properly install the workspace.

## Verification

After the fix:

```bash
docker compose --env-file .env.docker.secret up --build -d
```

All containers should be up:

- backend — Up
- caddy — Up
- pgadmin — Up
- postgres — Up (healthy)

## Key Insight

When using uv workspaces with multi-stage Docker builds:

1. **First stage** (`--no-install-project`): All `pyproject.toml` files must be mounted for dependency resolution
2. **Second stage** (full install): All project files must be copied before running `uv sync --locked`

The workspace structure requires uv to see all member projects to resolve dependencies correctly.

## Related

- [uv Docker documentation](https://docs.astral.sh/uv/guides/integration/docker/)
- [uv workspace documentation](https://docs.astral.sh/uv/concepts/projects/workspaces/)
