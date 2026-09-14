FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv==0.9.28

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev --no-editable

CMD ["/app/.venv/bin/orderbook-app"]
