FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY . .
RUN mkdir -p /app/models /app/data
RUN chmod +x entrypoint.sh
EXPOSE 8000
CMD ["./entrypoint.sh"]
