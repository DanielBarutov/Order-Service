FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY alembic.ini ./
COPY alembic/ ./alembic

COPY src/ ./src/
COPY main.py ./
RUN uv sync --frozen --no-cache

RUN chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app

CMD ["sh", "-c", "uv run alembic upgrade head && uv run python -m main"]