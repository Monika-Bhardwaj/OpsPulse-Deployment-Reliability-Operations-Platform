# ============================================================
# Stage 1: Builder
# Install application dependencies outside the runtime image.
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Use a pinned installer in the builder only.
RUN python -m pip install --no-cache-dir --upgrade pip==26.2.1

COPY requirements.txt .

# Install application dependencies into an isolated directory.
RUN python -m pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt

# Validate installed dependency consistency.
RUN python -m pip check


# ============================================================
# Stage 2: Runtime
# Only application dependencies and application code are copied.
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Apply available OS package upgrades and clean apt metadata.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the installed application dependencies from the builder.
COPY --from=builder /install /usr/local

# Copy application and migration files.
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

# Remove pip and its command-line entry points from runtime.
# Dependencies remain installed under /usr/local.
RUN rm -rf \
    /usr/local/lib/python3.12/site-packages/pip \
    /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
    /usr/local/bin/pip \
    /usr/local/bin/pip3 \
    /usr/local/bin/pip3.12 \
    /root/.cache/pip

# Run as a non-root user.
USER 10001

EXPOSE 8000

# Run migrations before starting the API.
# For multiple replicas, run migrations as a separate deployment job.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
