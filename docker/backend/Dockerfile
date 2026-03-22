FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg3 (libpq) and health checks (wget)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies (code comes via bind mount at runtime)
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

ENV GUNICORN_WORKER_CLASS=eventlet

CMD ["gunicorn", "-c", "config/gunicorn.conf.py", "wsgi:app"]
