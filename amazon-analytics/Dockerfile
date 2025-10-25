FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/uploads data/processed data/exports data/cache data/db

# Expose port
EXPOSE 8000

# Run the application with gunicorn + uvicorn workers
# Optimized for NAS environment: reduced workers from 4 to 2 for lower memory usage
CMD ["gunicorn", "app.api.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "600", "--log-level", "info"]

