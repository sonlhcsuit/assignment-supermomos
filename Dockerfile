FROM python:3.13-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy lock file and project configuration for better caching
COPY uv.lock pyproject.toml ./

# Sync dependencies from lock file (frozen, no dev dependencies)
RUN uv sync --frozen --no-dev

# Copy complete project
COPY . .

# Install project in editable mode (if needed)
RUN uv pip install --no-deps -e .

# Build stage
FROM python:3.13-slim AS runtime

# Install uv in the runtime image
RUN pip install --no-cache-dir uv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    POLARS_SKIP_CPU_CHECK=true

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . .

# Allow execution of the startup script
RUN chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]

# Expose port for FastAPI
EXPOSE 8000