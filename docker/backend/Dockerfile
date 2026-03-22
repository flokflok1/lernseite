FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies (code comes via bind mount at runtime)
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

ENV GUNICORN_WORKER_CLASS=eventlet

CMD ["gunicorn", "-c", "config/gunicorn.conf.py", "wsgi:app"]
