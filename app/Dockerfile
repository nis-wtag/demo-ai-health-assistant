# -------------------------
# Stage 1: Builder
# -------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# -------------------------
# Stage 2: Runtime
# -------------------------
FROM python:3.12-slim AS runner

WORKDIR /app

# Install uv in runtime
RUN pip install --no-cache-dir uv debugpy fastapi psycopg2-binary sqlalchemy uvicorn

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code
COPY . .

# Make script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Run the start script
CMD ["./start.sh"]