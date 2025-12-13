"""
LernsystemX Backend - Gunicorn Production Configuration

This file configures Gunicorn WSGI server for production deployment.

Usage:
    gunicorn -c gunicorn.conf.py "app:create_app()"

Environment Variables:
    GUNICORN_WORKERS - Number of worker processes (default: CPU count * 2 + 1)
    GUNICORN_THREADS - Number of threads per worker (default: 2)
    GUNICORN_TIMEOUT - Worker timeout in seconds (default: 120)
    GUNICORN_KEEPALIVE - Keep-alive timeout (default: 5)
    GUNICORN_BIND - Bind address (default: 0.0.0.0:8000)
    LOG_LEVEL - Logging level (default: info)

ISO 27001:2013 compliant - Production server configuration
"""

import os
import multiprocessing

# Server Socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker Processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gthread')
threads = int(os.getenv('GUNICORN_THREADS', 2))
worker_connections = 1000
max_requests = 10000  # Restart workers after serving this many requests
max_requests_jitter = 1000  # Add randomness to max_requests
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', 5))

# Process Naming
proc_name = 'lsx-backend'

# Server Mechanics
daemon = False  # Don't daemonize (systemd handles this)
pidfile = None  # systemd manages the pid
user = None  # Run as current user (systemd sets this)
group = None
umask = 0
tmp_upload_dir = None

# Logging
accesslog = '-'  # Log to stdout (captured by systemd)
errorlog = '-'  # Log to stderr (captured by systemd)
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
def worker_int(worker):
    """Called when a worker receives a SIGINT or SIGQUIT signal"""
    worker.log.info("Worker received INT or QUIT signal")


def worker_abort(worker):
    """Called when a worker receives a SIGABRT signal"""
    worker.log.info("Worker received SIGABRT signal")


def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")


def pre_exec(server):
    """Called just before a new master process is forked"""
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Server is ready. Spawning workers")


def worker_exit(server, worker):
    """Called just after a worker has been exited"""
    server.log.info(f"Worker exited (pid: {worker.pid})")


def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed"""
    server.log.info(f"Number of workers changed from {old_value} to {new_value}")


# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# X-Forwarded-* headers
forwarded_allow_ips = '*'  # Trust all proxies (Nginx is in front)

# SSL (handled by Nginx, but can be enabled here if needed)
# keyfile = None
# certfile = None
