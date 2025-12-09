# Multi-stage Dockerfile for Release Copilot API

# Stage 1: Builder
FROM python:3.13-slim as builder

WORKDIR /app

# Install uv and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files first (for layer caching)
COPY pyproject.toml ./

# Copy source code (needed for -e . installation)
COPY src/ ./src/
COPY README.md ./

# Install dependencies using uv
RUN uv pip install --system --no-cache -e .

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Create non-root user first
RUN useradd -m -u 1000 appuser

# Install uv globally for all users
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv* /usr/local/bin/

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and data
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser pyproject.toml README.md ./

# Create necessary directories
RUN mkdir -p data traces && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the API
CMD ["uvicorn", "rc_agent.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
