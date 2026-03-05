# ────────────────────────────────────────────────────────
#  Multi-stage build — lean production image
# ────────────────────────────────────────────────────────

FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ── Dependencies layer (cached unless requirements.txt changes) ──────────────
FROM base AS deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ── Final image ───────────────────────────────────────────────────────────────
FROM base AS final
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY src/ ./src/

EXPOSE 8000

# Run Alembic migrations then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
