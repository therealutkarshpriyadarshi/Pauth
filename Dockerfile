# Multi-stage Dockerfile for PAuth OAuth Library
# Stage 1: Base image with Python and Poetry
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Verify Poetry installation
RUN poetry --version

# Stage 2: Build dependencies
FROM base as builder

WORKDIR $PYSETUP_PATH

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies only (no dev dependencies)
RUN poetry install --no-dev --no-root && \
    poetry cache clear pypi --all

# Stage 3: Development image
FROM base as development

WORKDIR $PYSETUP_PATH

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install all dependencies including dev dependencies
RUN poetry install --no-root

# Set working directory for application
WORKDIR /app

# Copy application code
COPY . /app/

# Install the package in editable mode
RUN poetry install

# Expose port for potential web services
EXPOSE 8000

# Default command: open interactive Python shell with pauth available
CMD ["python", "-c", "from src.client import OAuth2Client; from src.models import Providers; print('PAuth development environment ready!'); import code; code.interact(local=locals())"]

# Stage 4: Production/Runtime image
FROM base as production

# Copy installed dependencies from builder
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

# Create app directory
WORKDIR /app

# Copy application code
COPY . /app/

# Create non-root user for security
RUN useradd -m -u 1000 pauth && \
    chown -R pauth:pauth /app

# Switch to non-root user
USER pauth

# Set Python path to include src directory
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import src; print('healthy')" || exit 1

# Default command: run basic example
CMD ["python", "-m", "src.examples.basic_example"]

# Stage 5: Testing image
FROM development as testing

WORKDIR /app

# Run tests
CMD ["poetry", "run", "pytest", "-v", "--cov=src", "--cov-report=term-missing"]

# Stage 6: Playground image for interactive OAuth testing
FROM development as playground

WORKDIR /app

# Expose port for OAuth callbacks
EXPOSE 5000 8000

# Run the OAuth playground
CMD ["python", "-m", "src.examples.playground_example"]
