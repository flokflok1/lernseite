"""Health Domain - System Health Checks

Minimalistic domain (no entities/repositories needed).
Only provides health check endpoints for monitoring.

Handles:
- Basic health check (/health)
- Detailed health check (/health/detailed)
- Database connectivity check
- Redis connectivity check
- Application uptime
"""
# Health checks are routes only - no domain entities
