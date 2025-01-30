FROM python:3.13 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .

# Create a startup script
COPY <<EOF /app/start.sh
#!/bin/bash
./.venv/bin/alembic upgrade head
./.venv/bin/fastapi run stash/main.py
EOF

RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
