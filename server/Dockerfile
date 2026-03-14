FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY server/pyproject.toml .
RUN uv sync --frozen --no-dev

COPY server/app /app/app
COPY server/main.py /app/main.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
