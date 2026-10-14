# ============================================================
# Stage 1: Builder
# Install runtime-only dependencies outside the final image.
# Test dependencies (pytest, httpx) stay out via requirements-prod.txt.
# ============================================================
FROM python:3.12-alpine AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Compilers and headers for source builds on musl (psycopg, uvloop).
RUN apk add --no-cache gcc musl-dev python3-dev postgresql-dev libffi-dev

COPY requirements-prod.txt ./requirements.txt

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
# Alpine base keeps the OS CVE surface minimal (0 HIGH/CRITICAL).
# ============================================================
FROM python:3.12-alpine AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Runtime C library for psycopg plus latest Alpine security patches.
RUN apk add --no-cache libpq \
    && apk upgrade --no-cache \
    && rm -rf /var/cache/apk/*

# Copy the installed application dependencies from the builder.
COPY --from=builder /install /usr/local

# Copy application and migration files.
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

# Remove pip and its command-line entry points from runtime.
# Dependencies remain installed under /usr/local.
RUN rm -rf \
    /usr/local/lib/python*/site-packages/pip \
    /usr/local/lib/python*/site-packages/pip-*.dist-info \
    /usr/local/bin/pip \
    /usr/local/bin/pip3* \
    /root/.cache/pip

# Run as a non-root user.
USER 10001

EXPOSE 8000

# Run migrations before starting the API.
# For multiple replicas, run migrations as a separate deployment job.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
