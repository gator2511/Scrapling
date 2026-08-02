FROM python:3.12-slim-trixie

LABEL io.modelcontextprotocol.server.name="io.github.D4Vinci/Scrapling"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency file first for better layer caching
COPY pyproject.toml ./

# Install dependencies only
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --all-extras --compile-bytecode

# Copy source code
COPY . .

# Install browsers and project in one optimized layer
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    uv run playwright install-deps chromium && \
    uv run playwright install chromium && \
    uv sync --all-extras --compile-bytecode && \
    uv run --no-sync python -c "from scrapling.core.ai import ScraplingMCPServer; ScraplingMCPServer()" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Expose port for MCP server HTTP transport
EXPOSE 8000

# Run the already-installed Scrapling package without resolving dependencies again
ENTRYPOINT ["uv", "run", "--no-sync", "scrapling"]

# Run the authenticated Streamable HTTP MCP server by default
CMD ["mcp", "--http", "--host", "0.0.0.0", "--port", "8000"]
