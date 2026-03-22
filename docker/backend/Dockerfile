FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg3 (libpq) and health checks (wget)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cache layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create data directories
RUN mkdir -p uploads logs data

EXPOSE 8000

# Worker class controlled by GUNICORN_WORKER_CLASS env var (read in wsgi.py)
ENV GUNICORN_WORKER_CLASS=eventlet

CMD ["gunicorn", "-c", "config/gunicorn.conf.py", "wsgi:app"]
