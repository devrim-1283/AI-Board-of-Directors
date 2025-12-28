FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# libpq-dev is required for psycopg2/asyncpg to build if wheels aren't valid
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set a non-root user for security (Optional but recommended)
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]
